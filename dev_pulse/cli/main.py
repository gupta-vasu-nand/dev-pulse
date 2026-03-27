"""Click CLI interface for Dev-Pulse."""

import click
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from datetime import datetime

from dev_pulse.core.config import config
from dev_pulse.core.logger import get_logger
from dev_pulse.services.metrics_service import metrics_service
from dev_pulse.services.cache_service import cache_service
from dev_pulse.utils.helpers import parse_date, validate_repo, get_default_since

logger = get_logger(__name__)
console = Console()


@click.group()
def cli():
    """Dev-Pulse - GitHub Developer Activity Analyzer."""
    pass


@cli.command()
@click.option('--repo', required=True, help='Repository (owner/repo)')
@click.option('--user', help='Filter by username')
@click.option('--since', help='Start date (YYYY-MM-DD)')
@click.option('--max-prs', default=50, help='Maximum PRs to analyze (default: 50)')
def analyze(repo: str, user: str, since: str, max_prs: int):
    """Analyze developer activity for a repository."""
    try:
        # Validate inputs
        if not validate_repo(repo):
            console.print("[red]Error: Invalid repository format. Use owner/repo[/red]")
            return
        
        if not config.validate_token():
            console.print("[red]Error: GitHub token not configured. Set GITHUB_TOKEN in .env[/red]")
            console.print("[yellow]Get a token at: https://github.com/settings/tokens[/yellow]")
            return
        
        # Parse date
        since_date = parse_date(since) if since else get_default_since()
        
        console.print(Panel.fit(
            f"[bold cyan]Analyzing Repository:[/bold cyan] {repo}\n"
            f"[bold cyan]Since:[/bold cyan] {since_date.strftime('%Y-%m-%d')}\n"
            f"[bold cyan]User Filter:[/bold cyan] {user or 'All users'}\n"
            f"[bold cyan]Max PRs:[/bold cyan] {max_prs}",
            title="Dev-Pulse Analysis"
        ))
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Fetching and analyzing data...", total=None)
            
            # Perform analysis
            metrics = metrics_service.analyze_activity(repo, since_date, user)
            summary = metrics_service.get_summary(metrics)
            
            progress.update(task, completed=True)
        
        # Display summary
        if metrics['total_contributors'] > 0:
            console.print("\n[bold green]Summary Statistics:[/bold green]")
            summary_table = Table(title="Activity Summary")
            summary_table.add_column("Metric", style="cyan")
            summary_table.add_column("Value", style="green")
            
            summary_table.add_row("Total Commits", str(summary['total_commits']))
            summary_table.add_row("PRs Opened", str(summary['total_prs_opened']))
            summary_table.add_row("PRs Merged", str(summary['total_prs_merged']))
            summary_table.add_row("Code Reviews", str(summary['total_reviews']))
            summary_table.add_row("Review Comments", str(summary['total_comments']))
            summary_table.add_row("Contributors", str(summary['total_contributors']))
            
            if summary.get('prs_processed', 0) < summary.get('total_prs', 0):
                summary_table.add_row(
                    "Note", 
                    f"Analyzed {summary['prs_processed']} of {summary['total_prs']} PRs for performance"
                )
            
            console.print(summary_table)
            
            # Display detailed metrics
            if metrics['metrics']:
                console.print("\n[bold green]Detailed Developer Metrics:[/bold green]")
                detail_table = Table(title="Developer Activity")
                detail_table.add_column("Developer", style="cyan")
                detail_table.add_column("Commits", justify="right", style="green")
                detail_table.add_column("PRs Opened", justify="right", style="yellow")
                detail_table.add_column("PRs Merged", justify="right", style="yellow")
                detail_table.add_column("Reviews", justify="right", style="magenta")
                detail_table.add_column("Comments", justify="right", style="magenta")
                
                for developer, dev_metrics in sorted(metrics['metrics'].items(), key=lambda x: x[1]['commits'], reverse=True)[:20]:  # Show top 20
                    detail_table.add_row(
                        developer[:30],  # Truncate long names
                        str(dev_metrics['commits']),
                        str(dev_metrics['prs_opened']),
                        str(dev_metrics['prs_merged']),
                        str(dev_metrics['reviews']),
                        str(dev_metrics['review_comments'])
                    )
                
                console.print(detail_table)
                
                if len(metrics['metrics']) > 20:
                    console.print(f"[dim]... and {len(metrics['metrics']) - 20} more contributors[/dim]")
        else:
            console.print("\n[yellow]No activity found for the specified criteria[/yellow]")
            console.print("[yellow]Try a different repository or date range[/yellow]")
        
        logger.info(f"Analysis completed for {repo}")
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Analysis interrupted by user[/yellow]")
        logger.info("Analysis interrupted by user")
    except Exception as e:
        logger.critical(f"Analysis failed: {e}", exc_info=True)
        console.print(f"\n[red]Error: {e}[/red]")
        console.print("[yellow]Check the logs in the logs/ directory for more details[/yellow]")


@cli.command()
def cache_status():
    """Display cache status."""
    try:
        status = cache_service.get_status()
        
        if 'error' in status:
            console.print(f"[red]Error getting cache status: {status['error']}[/red]")
            return
        
        console.print(Panel.fit(
            f"[bold cyan]Cache Status[/bold cyan]\n\n"
            f"Total Entries: {status['total_entries']}\n"
            f"Expired Entries: {status['expired_entries']}\n"
            f"TTL: {status['ttl_hours']} hours\n\n"
            f"[bold]By Endpoint:[/bold]",
            title="Cache Status"
        ))
        
        if status['by_endpoint']:
            for endpoint, count in list(status['by_endpoint'].items())[:10]:  # Show top 10
                console.print(f"  • {endpoint}: {count} entries")
            if len(status['by_endpoint']) > 10:
                console.print(f"  ... and {len(status['by_endpoint']) - 10} more endpoints")
        else:
            console.print("  No cached entries")
        
        # Cleanup expired entries
        deleted = cache_service.cleanup_expired()
        if deleted:
            console.print(f"\n[green]Cleaned up {deleted} expired entries[/green]")
            
    except Exception as e:
        logger.error(f"Failed to get cache status: {e}")
        console.print(f"[red]Error: {e}[/red]")


@cli.command()
@click.option('--endpoint', help='Clear cache for specific endpoint only')
def clear_cache(endpoint: str):
    """Clear the cache."""
    try:
        deleted = cache_service.clear(endpoint)
        if deleted > 0:
            console.print(f"[green]Successfully cleared {deleted} cache entries[/green]")
        else:
            console.print("[yellow]No cache entries to clear[/yellow]")
        logger.info(f"Cache cleared: {deleted} entries removed")
        
    except Exception as e:
        logger.error(f"Failed to clear cache: {e}")
        console.print(f"[red]Error: {e}[/red]")


def main():
    """Main entry point."""
    cli()


if __name__ == '__main__':
    main()