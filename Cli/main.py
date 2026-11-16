# awscan CLI entry point
import json

import click
from tabulate import tabulate

from Core.banner import print_banner
from Core import orchestrator


@click.command()
@click.option('--profile', help='AWS CLI profile to use (default credential chain if no keys are given).')
@click.option('--access-key', help='AWS access key ID (optional; prefer --profile or environment variables).')
@click.option('--secret-key', help='AWS secret access key (prompted securely if --access-key is given).')
@click.option('--session-token', default=None, help='AWS session token, for temporary credentials only.')
@click.option('--region', default='us-east-1', show_default=True, help='AWS region to use.')
@click.option(
    '--output',
    type=click.Choice(['table', 'json'], case_sensitive=False),
    default='table',
    help='Output format for the results (table or json).'
)
def main(profile, access_key, secret_key, session_token, region, output):
    """Audit an AWS account against CIS AWS Foundations Benchmark controls."""
    json_mode = output.lower() == 'json'  # keep stdout pure JSON in json mode
    if not json_mode:
        print_banner()
    if access_key and not secret_key:
        secret_key = click.prompt('Enter your secret key', hide_input=True)

    # 1) Validate & discover
    valid, response, session = orchestrator.validate_creds(
        access_key, secret_key, session_token, region, profile=profile
    )
    if not valid:
        raise click.ClickException(response)
    click.echo(response, err=json_mode)

    click.echo("Discovering enabled services...", err=json_mode)
    enabled_services = orchestrator.discover_enabled_services(session)
    click.echo(f"Found {len(enabled_services)} services: {', '.join(enabled_services)}\n", err=json_mode)

    # 2) Run audits
    click.echo("Running CIS benchmarks…", err=json_mode)
    all_results = orchestrator.thread_audits(enabled_services, session)
    consolidated = orchestrator.organize_results(all_results)

    # 3) Render output
    if json_mode:
        click.echo(json.dumps(consolidated, indent=2, default=str))
    else:
        headers = ['check_id', 'status', 'resource', 'evidence', 'remediation']
        for service, findings in consolidated.items():
            click.echo(click.style(f"\n=== {service.upper()} ===", fg="yellow", bold=True))
            rows = [[f.get(h, '') or '' for h in headers] for f in findings]
            click.echo(tabulate(rows, headers=headers, tablefmt='grid'))


if __name__ == '__main__':
    main()
