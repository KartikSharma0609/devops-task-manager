# 🚀 DevOps Task Manager

A production-style **REST API** (Flask + PostgreSQL) deployed on **AWS** with a fully automated, **infrastructure-as-code** pipeline: Docker, Nginx, Amazon ECR, Terraform with remote state, GitHub Actions using **OIDC (no long-lived AWS keys)**, and CloudWatch monitoring with alerting.

This project covers the whole lifecycle: **code → test → container → registry → infrastructure → deploy → monitor → alert.**

> **Live demo** (public IP changes when the instance is stopped/started, since no Elastic IP is used to keep costs at zero):
> API: `http://3.110.136.168/` · Swagger UI: `http://3.110.136.168/docs`
> Current IP: `terraform output ec2_public_ip`

---

## 📑 Table of Contents

1. [What This Project Demonstrates](#-what-this-project-demonstrates)
2. [Tech Stack](#-tech-stack)
3. [End-to-End Architecture](#-end-to-end-architecture)
4. [Request Flow](#-request-flow)
5. [Application Design](#-application-design)
6. [CI/CD Pipeline](#-cicd-pipeline)
7. [Infrastructure as Code (Terraform)](#-infrastructure-as-code-terraform)
8. [Security Model](#-security-model)
9. [Monitoring & Alerting](#-monitoring--alerting)
10. [Cost Control](#-cost-control)
11. [Project Structure](#-project-structure)
12. [Local Development](#-local-development)
13. [API Reference](#-api-reference)
14. [Operations Runbook](#-operations-runbook)
15. [Troubleshooting Stories](#-troubleshooting-stories)
16. [Roadmap](#-roadmap)
17. [Author](#-author)

---

## ✨ What This Project Demonstrates

| Area | What's implemented |
|---|---|
| **Backend** | Flask-RESTX API, JWT auth, user-scoped CRUD, Alembic migrations, Swagger docs |
| **Containers** | Multi-container stack (app, Nginx, Postgres) with Docker Compose, hardened containers |
| **Registry** | Images built and pushed to **Amazon ECR**, tagged by commit SHA |
| **IaC** | EC2, IAM, security group, ECR, CloudWatch, SNS, SSM all defined in **Terraform** |
| **State** | Remote state in **S3** with native lockfile locking |
| **CI/CD** | GitHub Actions: test, plan on every push/PR, gated apply only when real changes exist |
| **Auth to AWS** | **GitHub OIDC** → IAM role (no static access keys stored in GitHub) |
| **Access to server** | **AWS Systems Manager**, no need to expose SSH publicly |
| **Observability** | CloudWatch Agent (CPU, memory, disk, container logs), dashboard, alarms → email via SNS |
| **Least privilege** | Scoped IAM policies for the CI role and the EC2 instance role |

---

## 🛠 Tech Stack

| Category | Technologies |
|---|---|
| Language / Framework | Python 3.13, Flask, Flask-RESTX |
| Database | PostgreSQL 17, SQLAlchemy, Alembic |
| Auth | Flask-JWT-Extended |
| Serving | Gunicorn, Nginx (reverse proxy) |
| Containers | Docker, Docker Compose |
| Cloud | AWS EC2, ECR, IAM, S3, SSM, CloudWatch, SNS, Route 53 health checks |
| IaC | Terraform (AWS provider `~> 6.0`, S3 backend) |
| CI/CD | GitHub Actions (OIDC to AWS) |
| Docs | Swagger / OpenAPI |

---

## 🏗 End-to-End Architecture

```mermaid
flowchart TB
    Dev([👨‍💻 Developer]) -->|git push / PR| GH[GitHub Repository]

    subgraph CICD[GitHub Actions]
        CI[App CI<br/>install · migrate · pytest]
        TF[Terraform Workflow<br/>fmt · validate · plan · apply]
    end

    GH --> CI
    GH --> TF

    TF -. OIDC token .-> IAMCI{{IAM Role<br/>GitHubActions-Terraform}}
    IAMCI --> AWS

    subgraph AWS[AWS ap-south-1]
        S3[(S3<br/>Terraform state<br/>+ lockfile)]
        ECR[(Amazon ECR<br/>task-manager images)]

        subgraph VPC[Default VPC · Public Subnet]
            subgraph EC2[EC2 t3.micro · Amazon Linux 2023]
                NGX[Nginx :80]
                APP[task-manager<br/>Gunicorn + Flask :5000]
                PG[(PostgreSQL 17)]
                CWA[CloudWatch Agent]
                SSMA[SSM Agent]
            end
            SG[Security Group<br/>80 open · 22 restricted]
        end

        subgraph OBS[Observability]
            CWM[CloudWatch Metrics<br/>DevOpsTaskManager]
            CWL[CloudWatch Logs<br/>/devops-task-manager/docker]
            DASH[Dashboard]
            ALM[Alarms]
            SNS[SNS Topic]
        end

        SSMS[Systems Manager<br/>Run Command · Association · Parameter Store]
    end

    TF <-->|state| S3
    TF -->|provisions| EC2
    TF -->|provisions| OBS
    TF -->|provisions| ECR
    ECR -->|docker pull via instance role| EC2
    NGX --> APP --> PG
    CWA --> CWM
    CWA --> CWL
    CWM --> DASH
    CWM --> ALM --> SNS -->|email| Dev
    SSMS <--> SSMA
    User([🌍 Client]) -->|HTTP :80| SG --> NGX
    R53([Route 53<br/>Health Check]) -->|GET /| SG
```

---

## 🔄 Request Flow

```mermaid
sequenceDiagram
    autonumber
    participant C as Client
    participant N as Nginx (:80)
    participant G as Gunicorn / Flask (:5000)
    participant J as JWT Auth
    participant D as PostgreSQL

    C->>N: POST /auth/login
    N->>G: proxy_pass
    G->>D: verify credentials
    D-->>G: user record
    G-->>C: 200 + JWT access token

    C->>N: GET /tasks (Authorization: Bearer JWT)
    N->>G: proxy_pass
    G->>J: validate token
    J-->>G: user identity
    G->>D: SELECT tasks WHERE user_id = me
    D-->>G: rows
    G-->>C: 200 + task list
```

Only Nginx is published on the host (`0.0.0.0:80`). The app (`5000`) and the database (`5432`) are reachable **only on the internal Docker network**.

---

## 🧩 Application Design

```mermaid
flowchart LR
    subgraph API[Flask-RESTX API]
        AUTH[/auth namespace<br/>register · login/]
        TASKS[/tasks namespace<br/>CRUD/]
        SYS[/system namespace<br/>health · db-test/]
    end
    AUTH --> SVC[Services layer]
    TASKS --> SVC
    SYS --> SVC
    SVC --> ORM[SQLAlchemy Models]
    ORM --> DB[(PostgreSQL)]
    MIG[Alembic migrations] --> DB
    JWT[Flask-JWT-Extended] --> AUTH
    JWT --> TASKS
```

**Container hardening** applied in production compose:
non-root user · read-only root filesystem · dropped Linux capabilities · `no-new-privileges` · environment-based secrets · container health checks against `/system/health`.

---

## ⚙ CI/CD Pipeline

There are two independent pipelines: one for **application code**, one for **infrastructure**.

### 1. Application CI

```mermaid
flowchart LR
    A[Push / PR] --> B[Checkout]
    B --> C[Install deps]
    C --> D[Start Postgres service]
    D --> E[Alembic upgrade]
    E --> F[pytest]
    F --> G{Pass?}
    G -- yes --> H[✅ Build OK]
    G -- no --> I[❌ Fail]
```

### 2. Infrastructure pipeline (Terraform)

One workflow, `terraform.yml`, runs on every push to `main` and every pull request that touches `terraform/**`.

```mermaid
flowchart TD
    A[Push / PR touching terraform/**] --> P

    subgraph P[Job 1: plan · no approval needed]
        P1[OIDC → assume IAM role] --> P2[terraform fmt -check]
        P2 --> P3[terraform init]
        P3 --> P4[terraform validate]
        P4 --> P5[terraform plan -out=tfplan]
        P5 --> P6{Real resource<br/>changes?}
    end

    P6 -- "No (e.g. only public_ip drift)" --> S[Apply job skipped<br/>no approval prompt]
    P6 -- Yes --> U[Upload tfplan artifact]
    U --> Q{Push to main?}
    Q -- "No (PR)" --> R[Stop: plan is the review]
    Q -- Yes --> G[⏸ Environment: production<br/>manual approval]
    G --> AP[Job 2: apply<br/>terraform apply tfplan]
    AP --> ST[(Update S3 state)]
```

**Key design decisions**

- **Plan is free, apply is gated.** Only the `apply` job uses the `production` GitHub Environment, so you're prompted to approve **only when infrastructure genuinely changes**.
- **Apply uses the exact reviewed plan** (`tfplan` artifact), so what was approved is what runs.
- **No AWS keys in GitHub.** Jobs exchange a short-lived GitHub OIDC token for temporary AWS credentials.
- **Cosmetic drift is ignored.** Restarting the instance changes its public IP; Terraform reports this as an output-only sync with *no real infrastructure change*, so the apply job does not trigger.

### OIDC trust model

```mermaid
sequenceDiagram
    participant GA as GitHub Actions job
    participant GHO as GitHub OIDC Provider
    participant STS as AWS STS
    participant R as IAM Role GitHubActions-Terraform

    GA->>GHO: Request ID token (id-token: write)
    GHO-->>GA: JWT (sub = repo:OWNER/REPO:...)
    GA->>STS: AssumeRoleWithWebIdentity(JWT)
    STS->>R: Check trust policy (aud + sub match)
    R-->>STS: allowed
    STS-->>GA: Temporary credentials (~1h)
    GA->>GA: terraform plan / apply
```

The role's trust policy uses `StringEquals` on `token.actions.githubusercontent.com:sub`, allowing only this repository's `main` branch, pull requests, and the `production` environment.

---

## 🏗 Infrastructure as Code (Terraform)

```mermaid
flowchart LR
    subgraph TFFILES[terraform/]
        E[ec2.tf]
        I[iam.tf]
        EC[ecr.tf]
        SG[security_group.tf]
        CW[cloudwatch.tf]
        AL[alarms.tf]
        V[variables.tf]
        O[outputs.tf]
        P[provider.tf]
    end
    P -->|backend s3| S3[(S3 state bucket)]
    E --> INST[EC2 instance]
    I --> ROLE[EC2 role + instance profile<br/>SSM · CloudWatch · ECR pull]
    EC --> REPO[ECR repository]
    SG --> SGR[Security group]
    CW --> PARAM[SSM Parameter<br/>agent config]
    CW --> ASSOC[SSM Association]
    CW --> DASH[Dashboard]
    AL --> TOPIC[SNS topic + email]
    AL --> ALARMS[4 CloudWatch alarms]
    ROLE --> INST
    SGR --> INST
```

| File | Manages |
|---|---|
| `provider.tf` | AWS provider, S3 backend (`use_lockfile = true`) |
| `ec2.tf` | `t3.micro` instance, encrypted 8 GB gp3 root volume, IMDSv2 required |
| `iam.tf` | EC2 role + instance profile: `AmazonSSMManagedInstanceCore`, `CloudWatchAgentServerPolicy`, scoped ECR pull |
| `ecr.tf` | ECR repository for the app image |
| `security_group.tf` | HTTP 80 open; SSH restricted to one CIDR |
| `cloudwatch.tf` | Agent config in SSM Parameter Store, SSM Association that deploys it, dashboard |
| `alarms.tf` | SNS topic + email subscription, CPU / memory / disk / status-check alarms |
| `variables.tf` / `outputs.tf` | Inputs (incl. `alert_email`) and outputs (IP, IDs, ECR URL) |

**State handling:** state lives in S3, not in git and not on anyone's laptop. Your terminal and GitHub Actions both read and write the same object, and the native lockfile prevents concurrent applies. `.terraform.lock.hcl` **is** committed to pin provider versions.

---

## 🔐 Security Model

```mermaid
flowchart TB
    subgraph Identities
        GHR[GitHubActions-Terraform role<br/>assumed via OIDC]
        EC2R[EC2-DevOpsTaskManager-SSM role<br/>instance profile]
    end

    GHR -->|inline scoped policy| TFR[Manage: EC2 · SG · ECR · IAM<br/>SNS · SSM · CloudWatch · S3 state]
    EC2R --> SSMP[AmazonSSMManagedInstanceCore]
    EC2R --> CWP[CloudWatchAgentServerPolicy]
    EC2R --> ECRP[ECR pull only<br/>on this repository]
```

| Layer | Control |
|---|---|
| CI → AWS | OIDC federation, short-lived credentials, trust policy pinned to this repo |
| CI permissions | Inline least-privilege policy, resource-scoped where AWS supports it |
| Instance | IMDSv2 enforced, encrypted EBS, role limited to SSM / CloudWatch / ECR pull |
| Network | Only port 80 public; SSH limited to a single CIDR; DB never exposed |
| Access | SSM Run Command / Session for administration |
| App | JWT auth, hashed passwords, user-scoped data access |
| Containers | Non-root, read-only FS, dropped capabilities, `no-new-privileges` |
| Secrets | Environment variables and GitHub secrets, `*.tfvars` and `*.tfstate` git-ignored |

---

## 📈 Monitoring & Alerting

```mermaid
flowchart LR
    EC2[EC2 host] --> CWA[CloudWatch Agent]
    DK[Docker JSON logs<br/>app · nginx · postgres] --> CWA
    CWA -->|metrics · 60s| M[(Namespace<br/>DevOpsTaskManager)]
    CWA -->|logs · 7-day retention| L[(Log group<br/>/devops-task-manager/docker)]
    HV[EC2 hypervisor] -->|free native metrics| N[(AWS/EC2)]

    M --> DB[Dashboard]
    N --> DB
    L --> DB

    M --> A1[disk > 85%]
    M --> A2[memory > 85%]
    M --> A3[CPU idle < 10%<br/>= usage > 90%]
    N --> A4[status check failed]
    A1 & A2 & A3 & A4 --> SNS[SNS] --> MAIL[📧 Email]
```

**Configuration is code.** The CloudWatch Agent JSON is stored in an SSM Parameter (`/devops-task-manager/cloudwatch-agent-config`) and delivered by an SSM Association, so there's no hand-edited config on the server.

| Signal | Source | Alarm |
|---|---|---|
| Memory used % | Agent | > 85% for 10 min |
| Disk used % (`/`) | Agent | > 85% for 10 min |
| CPU idle % | Agent (`cpu-total` dimension) | < 10% for 10 min |
| Instance status check | Native `AWS/EC2` | > 0 for 2 min |
| Container logs | Agent → CloudWatch Logs | n/a (7-day retention) |

The disk alarm has already caught a real issue: 26 Docker images had accumulated on an 8 GB volume (88% used). Pruning unused images brought it back to normal.

---

## 💰 Cost Control

| Decision | Reason |
|---|---|
| `t3.micro`, single instance | Minimal compute |
| Only 3 custom metrics (`mem`, `disk`, `cpu_usage_idle`) | Custom metrics are ~$0.30/metric/month |
| Native EC2 CPU metric on dashboard | Free |
| 4 alarms, 1 dashboard, 1 SNS topic | Within free tiers |
| 7-day log retention | Keeps log storage negligible |
| No Elastic IP | Avoids idle-IP charges (trade-off: IP changes on stop/start) |
| S3 for state | A few KB, effectively free |

Estimated monitoring cost: **under $1/month**. The instance and EBS volume are the main spend.

---

## 📁 Project Structure

```
.
├── .github/workflows/     # CI and Terraform pipelines
├── app/                   # Flask application (api, models, services, utils)
├── migrations/            # Alembic migrations
├── nginx/                 # Nginx reverse-proxy config
├── terraform/             # All AWS infrastructure as code
│   ├── provider.tf        # provider + S3 backend
│   ├── ec2.tf  iam.tf  ecr.tf  security_group.tf
│   ├── cloudwatch.tf  alarms.tf
│   ├── variables.tf  outputs.tf
│   └── .terraform.lock.hcl
├── tests/                 # pytest suite
├── docs/images/           # Screenshots
├── Dockerfile
├── docker-compose.yml         # development
├── docker-compose.prod.yml    # production
├── app.py  start.sh  init-db.sql
├── requirements.txt  pyproject.toml
└── README.md
```

---

## 🚀 Local Development

```bash
git clone https://github.com/KartikSharma0609/devops-task-manager.git
cd devops-task-manager

python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

# create a .env file with your database and JWT settings
flask db upgrade
python app.py
```

**With Docker**

```bash
# development
docker compose up --build

# production-style
docker compose -f docker-compose.prod.yml up --build -d
```

**Tests**

```bash
pytest
```

Covers authentication, task CRUD, protected endpoints, database connectivity and health checks.

---

## 📚 API Reference

Interactive docs are served at **`/docs`** (Swagger UI). Protected endpoints require:

```
Authorization: Bearer <JWT_TOKEN>
```

| Group | Method | Endpoint | Auth |
|---|---|---|---|
| Auth | POST | `/auth/register` | No |
| Auth | POST | `/auth/login` | No |
| Tasks | GET | `/tasks` | Yes |
| Tasks | POST | `/tasks` | Yes |
| Tasks | PUT | `/tasks/{id}` | Yes |
| Tasks | DELETE | `/tasks/{id}` | Yes |
| System | GET | `/system` | No |
| System | GET | `/system/health` | No |
| System | GET | `/system/db-test` | No |

---

## 🧰 Operations Runbook

**Get the current public IP** (changes on every stop/start)

```bash
cd terraform && terraform output ec2_public_ip
```

**Run a command on the instance via SSM**

```bash
CMD=$(aws ssm send-command --region ap-south-1 \
  --instance-ids <INSTANCE_ID> --document-name AWS-RunShellScript \
  --parameters 'commands=["docker ps"]' --query Command.CommandId --output text)

aws ssm get-command-invocation --region ap-south-1 \
  --command-id "$CMD" --instance-id <INSTANCE_ID> \
  --query "[Status,StandardOutputContent,StandardErrorContent]" --output table
```

**Check alarms**

```bash
aws cloudwatch describe-alarms --region ap-south-1 --alarm-name-prefix task-manager \
  --query "MetricAlarms[].{Name:AlarmName,State:StateValue}" --output table
```

**Pause / resume the CloudWatch Agent**

```bash
sudo systemctl stop amazon-cloudwatch-agent && sudo systemctl disable amazon-cloudwatch-agent
sudo systemctl enable  amazon-cloudwatch-agent && sudo systemctl start amazon-cloudwatch-agent
```

**Reclaim disk space**

```bash
docker system df
docker image prune -af
```

**Confirm the SSM Association applied**

```bash
aws ssm list-associations --region ap-south-1 \
  --association-filter-list key=Name,value=AmazonCloudWatch-ManageAgent
```

---

## 🩺 Troubleshooting Stories

Real problems hit and solved while building this project.

<details>
<summary><b>1. SSM agent showed <code>ConnectionLost</code>; commands stuck in Pending</b></summary>

Worked through the layers in order: instance profile and IAM policies → security group egress → route table (found via the VPC's main table) → network ACLs → the instance itself. AWS-side config was all correct. Getting a shell through EC2 Instance Connect showed the agent had recovered after a restart and DNS, TLS and clock were healthy. Lesson: verify each layer with evidence before changing anything.
</details>

<details>
<summary><b>2. GitHub OIDC: <code>Not authorized to perform sts:AssumeRoleWithWebIdentity</code></b></summary>

The role's trust policy allowed only `repo:...:environment:production`. Workflows whose job did not declare that environment produced a different `sub` claim and were rejected. Fixed by explicitly allowing the `main` ref and `pull_request` subjects, and by making only the apply job use the environment.
</details>

<details>
<summary><b>3. Approval prompt on every push, even with no infra change</b></summary>

Split into a plan job (ungated) and an apply job (gated by the `production` environment) that runs only when the plan contains real changes. A restart-induced `public_ip` change is state-only and correctly skipped.
</details>

<details>
<summary><b>4. Terraform apply failed with AccessDenied, one action at a time</b></summary>

Terraform's AWS provider calls extra read APIs (`ListTagsForResource`, `DescribeParameters`, `GetSubscriptionAttributes`). `ssm:CreateAssociation` also needs permission on the **instance** and the **SSM document**, not just the association. The IAM policy was extended iteratively, and the partially created SNS subscription was auto-tainted and cleanly recreated.
</details>

<details>
<summary><b>5. CPU alarm stuck in <code>INSUFFICIENT_DATA</code> while data existed</b></summary>

With `totalcpu: true`, the agent publishes `cpu_usage_idle` with an extra dimension `cpu=cpu-total`. CloudWatch matches dimensions exactly, so an alarm defined with only `InstanceId` never sees the data. Fixed by adding the dimension to the alarm and dashboard widget. Found with `list-metrics`.
</details>

<details>
<summary><b>6. Disk alarm fired at 88%</b></summary>

`docker system df` showed 26 images (3 active), ~2.9 GB reclaimable from old CI/CD builds. Pruning resolved it; follow-up is automated cleanup after deploy.
</details>

---

## 🚧 Roadmap

- [ ] CloudTrail (management events) via Terraform
- [ ] S3 state bucket versioning + scheduled state backup
- [ ] Automated `docker image prune` after each deploy
- [ ] Larger root volume via Terraform
- [ ] Replace broad admin user permissions with a scoped policy
- [ ] HTTPS (ACM + load balancer or Let's Encrypt) and a domain name
- [ ] Refresh tokens, RBAC, rate limiting, API versioning (`/api/v1`)
- [ ] Prometheus + Grafana, Kubernetes / Helm

---

## 👨‍💻 Author

**Kartik Sharma** — Aspiring DevOps Engineer

- GitHub: [KartikSharma0609](https://github.com/KartikSharma0609)
- LinkedIn: [kartik-sharma-54328437a](http://www.linkedin.com/in/kartik-sharma-54328437a)

⭐ If this project helped you, consider giving it a star.
