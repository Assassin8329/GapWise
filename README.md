# GapWise — AI-Powered Learning Platform & Career Navigator

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.9+](https://img.shields.io/badge/Python-3.9%2B-brightgreen.svg)](https://www.python.org/)
[![Security: AES--256--GCM](https://img.shields.io/badge/Token%20Vault-AES--256--GCM-success.svg)](core/crypto_vault.py)
[![OAuth: PKCE S256](https://img.shields.io/badge/OAuth%202.0-RFC%207636%20PKCE-blueviolet.svg)](core/generic_connectors.py)

**GapWise** is an intelligent, adaptive career navigation and skill gap closure platform designed for **students**, **job seekers**, and **working professionals**. It identifies skill discrepancies, builds personalized visual learning roadmaps toward target roles, provides live adaptive testing and mock interviews, and dynamically recalibrates when personal goals, study rates, or schedules shift.

---

## 🎯 Goal & Problem Statement

Modern learners struggle with disconnected roadmaps, uncalibrated self-assessments, and rigid curricula that ignore life events:
- **Skill Blindspots**: Learners often experience the **Dunning-Kruger effect** (overestimating proficiency) or **Imposter Syndrome** (underestimating mastery).
- **Static Roadmaps**: When career goals or exams shift, roadmaps fail to adapt.
- **Account Privacy & Credential Leakage**: Traditional platforms store central API keys or expose raw user tokens to client-side code.

**GapWise solves this** through:
1. Deep skill analysis comparing current capabilities against industry career benchmarks.
2. An interactive **visual dependency graph (DAG)** that unlocks advanced topics as prerequisites are mastered.
3. A **NIST SP 800-38D compliant Token Vault** using **AES-256-GCM** encryption with unique per-user data keys, ensuring user credentials never leak to the browser or server logs.

---

## 🏗️ Architecture & Core Components

```
GapWise/
├── server.py                 # Threading HTTPServer & REST API router (Zero external dependencies)
├── config/
│   └── kms.json              # Simulated KMS Key Management Storage (Master Key store)
├── connectors/               # Generic Connector Framework configs (JSON-driven)
│   ├── github.json           # GitHub Repos & Commit activity
│   ├── linkedin.json         # LinkedIn Verified skills & experience
│   ├── google.json           # Google Auth & Calendar scheduling
│   ├── coursera.json         # Coursera Course credentials
│   ├── udemy.json            # Udemy Enrolled tracks
│   ├── notion.json           # Notion Study workspace exporter
│   ├── microsoft.json        # Microsoft Learn trophies & badges
│   └── custom_template.json  # Plug-and-play template for ANY OAuth 2.0 PKCE provider
├── core/
│   ├── aes_gcm.py            # Pure-Python AES-256-GCM cipher with Galois Field GF(2^128) arithmetic
│   ├── crypto_vault.py       # AES-256-GCM Token Vault, PBKDF2 data keys & Log Scrubber
│   ├── generic_connectors.py # Dynamic connector loader, RFC 7636 PKCE S256 engine & Proxy
│   ├── models.py             # UserProfile, Career benchmarks (Full Stack, AI/ML, DevOps, Data Science)
│   ├── skill_engine.py       # Gap analysis, Career matching, Confidence Meter, Struggle Detector
│   ├── roadmap_engine.py     # DAG dependency graph, Unlock paths, Career Pivot Simulator & diff
│   ├── test_engine.py        # Item Response Theory (IRT) adaptive test engine & Code Sandbox
│   ├── interview_engine.py   # Multi-dimensional rubric mock interview evaluator
│   ├── ai_mentor.py          # Ada AI Mentor chat, Weekly check-in diagnostic, Explain-Back Mode
│   ├── gamification.py       # XP, Levels, Titles, Badges, Personalized Quests, Opt-in Leaderboard
│   ├── analytics.py          # Learning Twin telemetry, Skill Passport, Ebbinghaus Skill Decay
│   └── scheduling.py         # Time-budget scheduling dynamically adapting around exams/crunch
├── data/
│   └── seed_data.py          # Realistic student, job seeker, and professional profiles & question banks
├── static/
│   ├── index.html            # Single Page Application (SPA) dashboard
│   ├── css/styles.css        # Responsive glassmorphism styling & visual graph layout
│   └── js/app.js             # Reactive client store & UI controller
└── tests/
    └── test_gapwise.py       # Automated unit test suite (Cryptography, Vault, IRT, DAG)
```

---

## 🌟 Key Features

### 1. User Profile & Adaptive Skill Matrix
- Supports three pre-configured personas (**Alex Chen - Senior CS Student**, **Maya Patel - Job Seeker Career Switcher**, **David Miller - Senior DevOps Pro**) or custom accounts.
- Self-rate skills (1–5 stars) with instant composite recalibration against assessed scores.

### 2. Career Matching & Skill Gap Analysis
- Benchmarks against live market roles: **Full Stack Developer**, **AI / ML Engineer**, **Cloud & DevOps Engineer**, and **Data Scientist**.
- Example: Compares Python, SQL, and HTML against Full Stack Developer, highlighting missing competencies: **JavaScript**, **React**, and **Node.js**.

### 3. Visual Dependency Graph (DAG) & Unlock Path
- Interactive SVG/node dependency graph.
- Enforces strict prerequisite logic: advanced modules (e.g., *Production React* or *Full Stack Capstone*) remain locked until foundational courses (e.g., *Modern JavaScript Deep Dive*) are mastered.
- Explains every recommendation with transparent *"Why this pick?"* rationales.

### 4. Confidence Meter (Self-Rated vs. Assessed)
- Detects the **Dunning-Kruger Effect** (high self-rating but lower assessment score).
- Identifies **Imposter Syndrome** (tested mastery exceeding self-perception).
- Flags calibrated skills where perception aligns with empirical performance.

### 5. AI Mentor (Ada) & Weekly Diagnostic Check-In
- Context-aware guidance incorporating current gaps and study habits.
- 3-question **Weekly Check-in** that recalibrates weekly hour budgets and injects remedial modules.
- **Explain-Back Mode (Feynman Technique)**: Learner teaches a concept in their own words; the agent evaluates conceptual accuracy, depth, clarity, and flags misconceptions.

### 6. Personalized Tests & Live Code Sandbox
- **Adaptive IRT Testing**: Uses Item Response Theory parameters ($a, b, c, \theta$). Slower learners receive smaller step sizes ($\Delta \theta$) and scaffolding hints; fast learners jump to synthesis challenges.
- **Micro-Quizzes in Code**: In-editor challenges embedded directly into code comments.
- **Live Code Sandbox**: In-browser Python 3 and JavaScript execution environment with unit test assertion reporting.

### 7. Personalized Mock Interview Agent
- Role-specific scenarios (e.g., Single Page App Architecture, Idempotent Payment APIs, Transformer Multi-Head Attention).
- Scored evaluations across **Technical Depth**, **Clarity**, **Problem Solving**, and **Communication**.

### 8. Career Pivot Simulator & Roadmap Diff
- What-if analysis: switch target role from Full Stack to AI/ML or Cloud Engineer.
- Computes exact skill overlap %, transferred skills efficiency, and newly required skills.

### 9. Learning Twin & Skill Decay Monitor
- **Learning Twin**: Digital twin mirroring study velocity (XP/day), retention stability, and peak focus hours.
- **Ebbinghaus Forgetting Curve**: Models retention decay ($R = e^{-t / S}$); triggers 2-minute refresher quizzes before retention dips below 75%.

### 10. Advanced Cohort & Academic Features
- **Skill Passport**: Cryptographically signed public credential link with SHA-256 digest.
- **Auto-Built Portfolio**: Automatically builds a showcase of completed projects with GitHub links and deploy URLs.
- **Cohort Heatmap**: Academic/university matrix highlighting collective team blindspots.
- **Time-Budget Scheduling**: Accommodates midterm exam weeks and work crunch sprints by automatically softening learning loads.

---

## 🔒 Security Architecture: Token Vault & Generic Connectors

### AES-256-GCM Token Vault
1. **Zero Owner Keys**: The platform never calls third-party APIs using its own developer keys. All calls run strictly using the user's personal vaulted credentials.
2. **KMS & PBKDF2 Data Keys**: Each user receives a unique derived 256-bit encryption key derived via PBKDF2-HMAC-SHA256 from the master KMS key and a user-specific salt.
3. **Zero Token Leakage**:
   - Access and refresh tokens are **never sent to the browser** (only sanitized status like `gho_***3f9` is returned).
   - Server logs run through an automated regex scrubber that intercepts and masks tokens (`[REDACTED_BY_TOKEN_VAULT]`).
4. **Server-Side Proxy**: Authorized agents make calls through `/api/proxy/:provider_id/:endpoint`, which injects vaulted tokens internally.

### Generic Connector Framework
Adding a new provider requires **zero code changes**—simply drop a JSON configuration into the `connectors/` folder:
```json
{
  "id": "github",
  "name": "GitHub",
  "auth_type": "oauth2_pkce",
  "auth_url": "https://github.com/login/oauth/authorize",
  "token_url": "https://github.com/login/oauth/access_token",
  "revoke_url": "https://api.github.com/applications/tokens/{token}",
  "api_base": "https://api.github.com",
  "scopes": ["read:user", "repo:status"],
  "scope_descriptions": {
    "read:user": "Reads your verified public username and profile info.",
    "repo:status": "Reads commit activity for skill verification."
  },
  "supports_pat": true
}
```
- **OAuth 2.0 with PKCE (RFC 7636)**: Generates high-entropy `code_verifier` and SHA-256 `code_challenge` (S256).
- **Personal Access Tokens (PAT)**: Supported for providers without OAuth.
- **Manual Import**: Ingests CSV or text credentials for platforms without public APIs.
- **Instant Revocation**: Disconnecting an account calls the provider's revocation endpoint and purges the key from the vault.

---

## 🚀 Quickstart & Setup

### Prerequisites
- Python 3.9+ (Built entirely on Python standard library — **no `pip install` required!**)
- Any modern web browser (Chrome, Firefox, Safari, Edge)

### 1. Launch the Server
```bash
cd /Users/shricharansrinivasan/GapWise
python3 server.py 8000
```

### 2. Access the Application
Open your browser and navigate to:
```
http://localhost:8000
```

### 3. Run the Automated Test Suite
```bash
python3 -m unittest discover -s tests -p "test_*.py"
```

Expected output:
```
.........
----------------------------------------------------------------------
Ran 9 tests in 0.049s

OK
```

---

## 📄 License

This project is licensed under the terms of the [MIT License](LICENSE).
