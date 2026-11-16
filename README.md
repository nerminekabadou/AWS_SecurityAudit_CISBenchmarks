# awscan: AWS CIS Benchmark Audit

[![tests](https://github.com/nerminekabadou/AWS_SecurityAudit_CISBenchmarks/actions/workflows/tests.yml/badge.svg)](https://github.com/nerminekabadou/AWS_SecurityAudit_CISBenchmarks/actions/workflows/tests.yml)

`awscan` checks an AWS account against controls from the **CIS AWS Foundations Benchmark** and reports every finding with its evidence and how to fix it. It runs as a command-line tool (table or JSON output) or as a small web app that keeps a history of scans and exports PDF reports.

## How it works

```
credentials ──▶ STS get-caller-identity (validation)
            ──▶ service discovery: IAM and monitoring are always audited;
                S3, EC2, EFS and RDS only if the account uses them
            ──▶ audits run in parallel (thread pool), one module per service
            ──▶ findings grouped by service ──▶ table | JSON | PDF report
```

Each check returns findings in the same shape: `check_id`, `status`, `resource`, `evidence`, `remediation`. If an audit module crashes, the error is reported as a finding instead of stopping the scan.

## Implemented checks

| Area | CIS controls |
|------|--------------|
| **IAM** | 1.1 avoid root account use · 1.2 MFA on root · 1.8 password length ≥ 14 · 1.9 password reuse prevention · 1.10 MFA for console users · 1.12 disable credentials unused for 45 days · 1.13 one active access key per user · 1.14 key rotation ≤ 90 days |
| **S3** | 2.1.1 default encryption · 2.1.2 deny non-HTTPS requests · 2.1.3 block public access |
| **RDS** | 2.2.x storage encryption, auto minor version upgrade, not publicly accessible |
| **EFS** | 2.3.1 encryption at rest |
| **EC2** | 2.7 default security group not in use · 2.13 no secrets in user data |
| **Monitoring** | 4.1 alarm on unauthorized API calls |
| **Logging** *(implemented, not yet enabled)* | 3.1–3.9 CloudTrail in all regions, log validation, AWS Config, KMS encryption and rotation, VPC flow logs, S3 object-level logging |

## Install

```bash
git clone https://github.com/nerminekabadou/AWS_SecurityAudit_CISBenchmarks.git
cd AWS_SecurityAudit_CISBenchmarks
pip install -e .
```

## Usage

```bash
awscan --profile audit --region eu-west-1            # use an AWS CLI profile
awscan --region us-east-1                            # default credential chain (env vars, SSO, instance role)
awscan --profile audit --output json > report.json   # machine-readable output
```

| Option | Description |
|--------|-------------|
| `--profile` | AWS CLI profile. If no keys are given, the standard credential chain is used |
| `--access-key`, `--secret-key`, `--session-token` | Explicit credentials. The secret is prompted securely if it's not passed |
| `--region` | Region to audit (default `us-east-1`) |
| `--output` | `table` (default) or `json`. In JSON mode only the report goes to stdout |

**Required permissions:** the AWS-managed `SecurityAudit` policy (read-only) covers all checks.

## Web interface

A React dashboard with a Flask API that runs scans, keeps a scan history and generates PDF reports (ReportLab).

```bash
pip install -e . -r webinterface/backend/requirements.txt
cd webinterface/frontend && npm install && npm start      # http://localhost:3000
cd webinterface/backend && flask --app app run             # http://localhost:5000
```

On Windows, `webinterface/build.ps1` starts both. The API is meant to run locally: it listens on `127.0.0.1` and only accepts requests from the local frontend.

## Project structure

```
Cli/main.py              awscan command (click)
Core/auth.py             credential validation (STS)
Core/orchestrator.py     service discovery and parallel audit execution
Core/Checks/*_audit.py   one module per service, one function per CIS control
webinterface/            Flask API + React dashboard, PDF reports
tests/                   unit tests (no AWS account needed)
```

### Adding a check
Add a `check_cis_x_y(session)` function to the right module in `Core/Checks/` that returns a list of findings, and call it from that module's `run_audit(session)`.

## Tests

```bash
pip install -r requirements-dev.txt
pytest
```

## Team
Team project. Nermine Kabadou ([@nerminekabadou](https://github.com/nerminekabadou)) wrote the IAM, S3, RDS, EFS and logging checks and the credential validation, together with Youssef Sahnoun, Achref Messai and Aziza Nagara.
