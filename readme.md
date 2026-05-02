# GameApp — AI-Powered DevSecOps Pipeline on AWS EKS

A Spring Boot web application (Snake game + Calculator + Auth) with a full **AI-augmented DevSecOps CI/CD pipeline** running on Jenkins, deployed to AWS EKS with HTTPS via Let's Encrypt.

---

## Table of Contents

1. [Application Overview](#application-overview)
2. [Tech Stack](#tech-stack)
3. [Pipeline Architecture](#pipeline-architecture)
4. [AI Layer — How It Works](#ai-layer--how-it-works)
5. [DevSecOps Stages](#devsecops-stages)
6. [Security Scanning](#security-scanning)
7. [Kubernetes Deployment & HTTPS](#kubernetes-deployment--https)
8. [Prerequisites](#prerequisites)
9. [Local Development](#local-development)
10. [Pipeline Setup](#pipeline-setup)
11. [Environment Variables & Credentials](#environment-variables--credentials)
12. [Project Structure](#project-structure)

---

## Application Overview

GameApp is a **Spring Boot MVC web application** that provides:

- User registration and login with session management (Spring Security + BCrypt)
- Personal dashboard per logged-in user
- Browser-based **Snake game** (canvas / JavaScript)
- Browser-based **Calculator** (JavaScript)
- H2 file-based database (no external DB required)

Live at: **https://quntamvector.in**

---

## Tech Stack

### Application

| Layer | Technology |
|---|---|
| Language | Java 17 |
| Framework | Spring Boot 3.5.0 |
| Security | Spring Security 6.5.0 |
| Persistence | Spring Data JPA + Hibernate 6 |
| Database | H2 (file mode — persistent local DB) |
| Templates | Thymeleaf 3.1.3 |
| Build Tool | Maven |
| Testing | JUnit 5, Mockito, MockMvc, Spring Boot Test (73 tests) |

### Infrastructure & DevSecOps

| Tool | Purpose |
|---|---|
| Jenkins | CI/CD orchestration |
| Docker | Container build and push |
| AWS EKS | Kubernetes cluster |
| SonarQube | Static code analysis |
| OWASP Dependency-Check | Dependency CVE scanning |
| Trivy | Container image vulnerability scanning |
| OPA / Conftest | Policy-as-code (Dockerfile + K8s manifests) |
| JaCoCo | Code coverage reports |
| cert-manager + Let's Encrypt | Automatic TLS certificate provisioning |
| NGINX Ingress | HTTPS termination and routing |

### AI / LLM

| Provider | Role |
|---|---|
| Ollama (Mistral — local) | Primary LLM, runs on the Jenkins server |
| HuggingFace free API | Fallback if Ollama is unavailable |
| OpenAI GPT-3.5 | Final fallback |

---

## Pipeline Architecture

```
Git Push
    │
    ▼
┌─────────────────────────────────────────────────────────────────┐
│                        JENKINS PIPELINE                         │
│                                                                 │
│  Git Checkout → Compile                                         │
│       │                                                         │
│       ▼                                                         │
│  ┌─────────────────────────────────┐                            │
│  │  AI LAYER 1 — Code Review       │  ← reads git diff          │
│  │  Catches: security bugs, bad    │     asks LLM to review     │
│  │  code patterns before tests run │     saves report.md        │
│  └─────────────────────────────────┘                            │
│       │                                                         │
│       ▼                                                         │
│  Test & Coverage (JaCoCo) → SonarQube → Quality Gate           │
│       │                                                         │
│       ▼                                                         │
│  OWASP Dependency Scan (CVE check on all Maven deps)            │
│       │                                                         │
│       ▼                                                         │
│  ┌──────────────────┐  ┌──────────────┐  ┌────────────────┐    │
│  │  Trivy Image Scan│  │ OPA Conftest │  │  Docker Build  │    │
│  │  (base image CVE)│  │ (policy lint)│  │                │    │
│  └──────────────────┘  └──────────────┘  └────────────────┘    │
│       │                                                         │
│       ▼                                                         │
│  ┌─────────────────────────────────┐                            │
│  │  AI LAYER 2 — Security Analysis │  ← reads OWASP JSON        │
│  │  Translates raw CVEs to plain   │     + trivy-report.txt     │
│  │  English executive report       │     asks LLM to summarise  │
│  └─────────────────────────────────┘                            │
│       │                                                         │
│       ▼                                                         │
│  Docker Push → Update Kubeconfig → OPA K8s Manifest Check      │
│       │                                                         │
│       ▼                                                         │
│  ┌─────────────────────────────────┐                            │
│  │  AI LAYER 3 — Release Notes     │  ← reads git log           │
│  │  Generates deployment docs from │     asks LLM to write      │
│  │  commit history automatically   │     professional notes     │
│  └─────────────────────────────────┘                            │
│       │                                                         │
│       ▼                                                         │
│  Deploy to EKS (kubectl apply)                                  │
└─────────────────────────────────────────────────────────────────┘
```

All AI stages use `catchError(UNSTABLE)` — if the LLM is unreachable, the pipeline continues and deploys. AI failures **never block CI/CD**.

---

## AI Layer — How It Works

### Shared Engine — `scripts/ai_utils.py`

Every AI stage calls `ask_llm(prompt)` which tries providers in order:

```
Ollama (Mistral on Jenkins server)  →  HuggingFace free API  →  OpenAI GPT-3.5
```

Before each LLM call, it checks Ollama's `/api/tags` endpoint — if the model isn't pulled locally, it pulls it once and caches it. Subsequent pipeline runs skip the download entirely.

---

### AI Layer 1 — Code Review (`scripts/ai_code_review.py`)

**Triggered:** After `mvn compile`, before tests.

**What it does:**
1. Runs `git diff HEAD~1 HEAD` to extract changed Java/Python/JS files
2. Sends the diff to the LLM as a security-focused code review prompt
3. Saves `ai-code-review-report.md` as a Jenkins artifact

**Report sections:**
- Summary of what changed
- Security Issues (CRITICAL / HIGH / MEDIUM / LOW)
- Code Quality Issues with fix suggestions
- What Was Done Well
- Top 3 Recommendations

**Why it helps:** Catches hardcoded secrets, SQL injection patterns, or insecure code **before the container is even built**.

---

### AI Layer 2 — Security Analysis (`scripts/ai_security_analysis.py`)

**Triggered:** After OWASP scan + Trivy scan.

**What it does:**
1. Parses `target/dependency-check-report.json` — extracts all CVEs with severity/CVSS scores
2. Reads `trivy-report.txt` — container image vulnerabilities
3. Sorts by severity, takes the top 15 most critical findings
4. Sends structured data to the LLM: *"Write an executive security report"*
5. Saves `ai-security-report.md` as a Jenkins artifact

**Report sections:**
- Executive Summary: *"Is this safe to deploy?"*
- Critical/High Findings — CVE ID, CVSS, what it enables, one-line fix
- Medium Priority — fix in next sprint
- Overall Risk Level (CRITICAL / HIGH / MEDIUM / LOW)
- Remediation Roadmap table (Quick Fix / 1 Sprint / Long Term)
- OWASP Top 10 mapping

**Why it helps:** Turns a raw 40-entry CVE JSON file into a 2-paragraph actionable report a non-security engineer can act on.

---

### AI Layer 3 — Release Notes (`scripts/ai_release_notes.py`)

**Triggered:** Just before `kubectl apply` (deploy).

**What it does:**
1. Gets commits since last git tag (or last 20 commits)
2. Gets list of files changed in the last 5 commits
3. Sends commit history + build metadata to the LLM
4. Saves `ai-release-notes.md` as a Jenkins artifact

**Report sections:**
- What's New
- Bug Fixes
- Security & Compliance Updates
- Infrastructure / Pipeline Changes
- Breaking Changes
- Deployment Checklist (checkboxes)

**Why it helps:** Commit messages like `"updated the ns"` are automatically translated into professional release documentation per build.

---

## DevSecOps Stages

| Stage | Tool | Fails Build? |
|---|---|---|
| Compile | Maven | Yes |
| AI Code Review | Ollama / HF / OpenAI | No (UNSTABLE) |
| Test & Coverage | JUnit + JaCoCo | Yes |
| SonarQube Analysis | SonarQube | Yes (Quality Gate) |
| OWASP Dependency Scan | dependency-check 12.x | UNSTABLE (CVSS ≥ 7.0) |
| Trivy Image Scan | Trivy | UNSTABLE (CRITICAL found) |
| OPA Dockerfile Policy | Conftest | Yes |
| Docker Build | Docker | Yes |
| AI Security Analysis | Ollama / HF / OpenAI | No (UNSTABLE) |
| Docker Push | Docker Hub | Yes |
| OPA K8s Manifest Policy | Conftest | Yes |
| AI Release Notes | Ollama / HF / OpenAI | No (UNSTABLE) |
| Deploy to EKS | kubectl | Yes |

---

## Security Scanning

### OWASP Dependency-Check

Scans all Maven dependencies for known CVEs using the NVD database.

**Key configuration (`pom.xml`):**

```xml
<failBuildOnCVSS>7</failBuildOnCVSS>                              <!-- fail on HIGH + CRITICAL -->
<ossindexAnalyzerEnabled>false</ossindexAnalyzerEnabled>           <!-- disable Sonatype (network issues) -->
<suppressionFile>owasp-suppressions.xml</suppressionFile>          <!-- NVD false positive suppressions -->
<nvdValidForHours>4</nvdValidForHours>                             <!-- skip NVD update if < 4h old -->
```

**False positive suppressions** (`owasp-suppressions.xml`) handle NVD CPE over-matching — for example, `spring-boot-starter-thymeleaf` being incorrectly tagged with Thymeleaf CVEs even though it's a Spring Boot auto-config JAR with no Thymeleaf code.

### Trivy

Scans the base Docker image (`eclipse-temurin:17-jdk`) for OS-level CVEs.

```bash
trivy image --severity HIGH,CRITICAL eclipse-temurin:17-jdk
```

### OPA / Conftest Policy-as-Code

Two policy files enforce security rules:

- `dockerfile-security.rego` — validates the Dockerfile (non-root user, no secrets, etc.)
- `opa-k8s-security.rego` — validates `deployment.yml` (resource limits, security contexts, etc.)

Both run via `openpolicyagent/conftest` Docker container — no host installation needed.

---

## Kubernetes Deployment & HTTPS

The app is deployed to AWS EKS in the `quantam` namespace.

### Architecture

```
Internet
    │  HTTPS :443
    ▼
AWS Load Balancer (provisioned by NGINX Ingress Controller)
    │
    ▼
NGINX Ingress Controller  ←── cert-manager (Let's Encrypt TLS cert)
    │
    │  quntamvector.in → fullstack-service:80
    ▼
fullstack-service (ClusterIP)
    │
    ▼
fullstack-deployment (3 replicas)
    │
    ▼
Pod: eclipse-temurin:17-jdk  →  gameapp-1.0.0.jar :8080
```

### Resources in `deployment.yml`

| Resource | Name | Purpose |
|---|---|---|
| Deployment | `fullstack-deployment` | 3 replicas of the Spring Boot app |
| Service | `fullstack-service` | ClusterIP — internal routing to pods |
| Ingress | `fullstack-ingress` | HTTPS termination, HTTP→HTTPS redirect |
| ClusterIssuer | `letsencrypt-prod` | ACME http01 challenge for certificate |

### TLS Certificate Flow

```
1. cert-manager sees Ingress annotation: cert-manager.io/cluster-issuer: "letsencrypt-prod"
2. ClusterIssuer contacts Let's Encrypt ACME server
3. Let's Encrypt sends http01 challenge to http://quntamvector.in/.well-known/acme-challenge/...
4. cert-manager creates a temporary Ingress rule to answer the challenge
5. Challenge passes → cert-manager creates TLS secret "fullstack-tls"
6. NGINX Ingress uses the secret for HTTPS termination
7. Certificate auto-renews every 60 days
```

### Prerequisites for HTTPS

```bash
# 1. Install NGINX Ingress Controller (creates the AWS Load Balancer)
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.10.0/deploy/static/provider/aws/deploy.yaml

# 2. Install cert-manager
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.14.0/cert-manager.yaml

# 3. Point your domain DNS to the Ingress Controller's AWS Load Balancer
# Get the external hostname:
kubectl get svc -n ingress-nginx ingress-nginx-controller
# Add a CNAME record: quntamvector.in → <EXTERNAL-HOSTNAME>

# 4. Apply the deployment (pipeline does this automatically)
kubectl apply -f deployment.yml -n quantam
```

---

## Prerequisites

### Jenkins Server

- Java 17
- Maven
- Docker
- `kubectl`
- AWS CLI (configured with EKS access)
- Python 3 (uses stdlib only — no pip install needed)
- [Ollama](https://ollama.com) with `mistral` model pulled:
  ```bash
  ollama pull mistral
  ```

### Jenkins Plugins

| Plugin | Purpose |
|---|---|
| Pipeline | Core pipeline support |
| Git | Source checkout |
| JaCoCo | Coverage reports |
| SonarQube Scanner | Code quality gate |
| OWASP Dependency-Check | CVE scanning + `dependencyCheckPublisher` |
| Kubernetes CLI | `withKubeConfig` step |
| Credentials Binding | Secret injection |

### Jenkins Credentials Required

| Credential ID | Type | Used For |
|---|---|---|
| `docker-hub-creds` | Username/Password | Docker Hub push |
| `hf-api-token` | Secret Text | HuggingFace API (AI fallback) |
| `openai-api-key` | Secret Text | OpenAI API (AI fallback) |
| `kube` | Secret File | kubectl kubeconfig for EKS |

---

## Local Development

```bash
# Clone the repository
git clone https://github.com/ManojKRISHNAPPA/SnakeGame.git
cd SnakeGame

# Run all 73 tests
mvn test

# Start the application (H2 file database, auto-created)
mvn spring-boot:run
# App at http://localhost:8080
# H2 console at http://localhost:8080/h2-console
#   JDBC URL: jdbc:h2:file:./data/gameapp | Username: sa | Password: (empty)

# Build a runnable JAR
mvn package
java -jar target/gameapp-1.0.0.jar

# Run AI scripts locally (requires Ollama running)
python3 scripts/ai_code_review.py
python3 scripts/ai_security_analysis.py
python3 scripts/ai_release_notes.py
```

---

## Pipeline Setup

### 1. Configure Ollama on the Jenkins Server

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull the model once (pipeline checks before each run — skips if already present)
ollama pull mistral

# Start on boot
systemctl enable ollama
```

### 2. Create a Jenkins Pipeline Job

1. New Item → **Pipeline**
2. Pipeline Definition: **Pipeline script from SCM**
3. SCM: Git → `https://github.com/ManojKRISHNAPPA/SnakeGame.git`
4. Branch: `ai-pipeline`
5. Script Path: `Jenkinsfile-ai`

### 3. Configure Tools in Jenkins

- **JDK**: Name `java-17` (install from Adoptium/Temurin)
- **Maven**: Name `maven` (install automatically)

### 4. SonarQube Setup

- Manage Jenkins → Configure System → SonarQube servers
- Name: `SonarQube`, URL: `http://<your-sonarqube-host>`
- Add SonarQube authentication token as a Jenkins credential

---

## Environment Variables & Credentials

Set in `Jenkinsfile-ai` environment block:

```groovy
OLLAMA_HOST         = "http://127.0.0.1:11434"  // Ollama API endpoint
OLLAMA_MODEL        = "mistral"                  // Model name (must be pulled)
AWS_REGION          = "ap-northeast-1"
CLUSTER_NAME        = "quantam-vector"
NAMESPACE           = "quantam"
AI_FAIL_ON_CRITICAL = "false"                    // Set "true" to block deploy on CRITICAL CVEs
```

---

## Project Structure

```
SnakeGame/
├── src/
│   ├── main/java/com/gameapp/
│   │   ├── GameAppApplication.java        # Spring Boot entry point
│   │   ├── config/SecurityConfig.java     # Auth rules, session, BCrypt
│   │   ├── controller/                    # AuthController, DashboardController
│   │   ├── model/User.java                # JPA entity → users table
│   │   ├── repository/UserRepository.java # Spring Data JPA queries
│   │   └── service/UserService.java       # Business logic
│   └── main/resources/templates/          # Thymeleaf HTML templates
├── scripts/
│   ├── ai_utils.py                        # LLM client: Ollama → HF → OpenAI
│   ├── ai_code_review.py                  # AI Layer 1: git diff → code review
│   ├── ai_security_analysis.py            # AI Layer 2: OWASP+Trivy → exec report
│   └── ai_release_notes.py                # AI Layer 3: git log → release notes
├── Jenkinsfile-ai                         # AI-augmented DevSecOps pipeline
├── Jenkinsfile                            # Standard DevSecOps pipeline
├── Jenkinsfile-production                 # Production pipeline
├── deployment.yml                         # K8s: Deployment + Service + Ingress + ClusterIssuer
├── dockerfile-security.rego               # OPA policy for Dockerfile
├── opa-k8s-security.rego                  # OPA policy for K8s manifests
├── owasp-suppressions.xml                 # NVD false positive suppressions
├── Dockerfile                             # eclipse-temurin:17-jdk, non-root user
├── pom.xml                                # Maven deps, OWASP plugin config
└── ARCHITECTURE.md                        # Deep-dive: layers, flows, test strategy
```

---

## AI Reports — Sample Output

Each build archives three markdown reports as Jenkins artifacts:

**`ai-code-review-report.md`** (Layer 1)
```
## Security Issues
[HIGH] Hardcoded database credentials found in UserService.java line 42
       Recommendation: move to application.properties or environment variable

## Top 3 Recommendations
1. Add input sanitisation before passing user data to JPA queries
2. Set SameSite=Strict on session cookie in SecurityConfig
3. Enable CSRF protection for state-changing endpoints
```

**`ai-security-report.md`** (Layer 2)
```
## Executive Summary
The application has 2 CRITICAL and 8 HIGH severity findings.
Deployment is NOT recommended until Tomcat and Spring Security
vulnerabilities are patched.

## Remediation Roadmap
| Priority   | Action                         | Effort  |
|------------|--------------------------------|---------|
| Quick Fix  | Upgrade Tomcat to 10.1.41      | 1 hour  |
| 1 Sprint   | Upgrade Spring Security 6.5.1  | 2 hours |
| Long Term  | Enable SAST scanning in pre-commit | 1 day |
```

**`ai-release-notes.md`** (Layer 3)
```
## What's New
- Added HTTPS support via NGINX Ingress and Let's Encrypt

## Security & Compliance Updates
- Upgraded Spring Boot from 3.4.3 to 3.5.0
- Added OWASP CVE suppression file for NVD false positives
- Fixed Sonatype OSS Index analyzer configuration

## Deployment Checklist
- [ ] All pipeline stages passed
- [ ] Security scan report reviewed
- [ ] Kubernetes manifests validated
- [ ] cert-manager ClusterIssuer applied to target namespace
```
