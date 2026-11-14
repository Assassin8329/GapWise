# GapWise — AI-Powered Learning Platform & Adaptive Career Navigator

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.9+](https://img.shields.io/badge/Python-3.9%2B-brightgreen.svg)](https://www.python.org/)
[![Security: AES--256--GCM](https://img.shields.io/badge/Token%20Vault-AES--256--GCM-success.svg)](core/crypto_vault.py)
[![OAuth: PKCE S256](https://img.shields.io/badge/OAuth%202.0-RFC%207636%20PKCE-blueviolet.svg)](core/generic_connectors.py)

**GapWise** is an intelligent, real-data-driven career navigation and skill gap closure web application. It identifies individual learner skill gaps, builds personalized visual roadmaps to target careers, tracks learning telemetry, and dynamically adapts when personal goals, study rates, or schedules shift.

---

## 🎯 Goal & Core Philosophy

- **Goal**: Find a learner's skill gaps. Build a personalized roadmap to a target career. Track progress. Adapt when goals or results change.
- **Target Users**: Students, job seekers, and working professionals. All users sign in with Google.
- **Strict Data Rule**:
  - **Zero fake, seeded, or mock data**.
  - Retains strictly real user profiles, real assessment attempts, and real external API credentials.
  - Graceful, informative **Empty States** when data has not yet been populated.

---

## 🏗️ Architecture & Project Structure

```
GapWise/
├── package.json              # Project descriptor, npm scripts & metadata (name: gapwise)
├── server.py                 # High-performance zero-dependency web server & REST API
├── config/
│   └── kms.json              # Key Management Storage (vault master key, gitignored)
├── connectors/               # Generic Connector Framework (JSON-driven, zero mock data)
│   ├── google.json           # Real Google OAuth 2.0 PKCE connector
│   ├── github.json           # GitHub code & project repos
│   ├── linkedin.json         # LinkedIn verified skills & experience
│   ├── coursera.json         # Coursera verified course certificates
│   ├── udemy.json            # Udemy student library & progress
│   ├── notion.json           # Notion study workspace export
│   ├── microsoft.json        # Microsoft Learn certifications
│   └── custom_template.json  # Drop-in template for ANY OAuth 2.0 PKCE provider
├── core/
│   ├── aes_gcm.py            # Pure-Python NIST SP 800-38D AES-256-GCM cipher
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
│   ├── store.py              # Persistent SQLite store for real users, attempts & sessions
│   ├── gapwise.db            # SQLite database file
│   └── seed_data.py          # Curriculum course catalog & evaluation schemas (no fake users)
├── static/
│   ├── index.html            # GapWise Single Page Application (SPA) dashboard
│   ├── css/styles.css        # Responsive glassmorphism styling & visual graph layout
│   └── js/app.js             # Reactive client store & UI controller
└── tests/
    └── test_gapwise.py       # Automated unit test suite (Cryptography, Vault, IRT, DAG, Store)
```

---

## 🌟 Key Capabilities

### 1. User Profile & Real Google Sign-In
- All users sign in with Google using **OAuth 2.0 with PKCE (RFC 7636)**.
- Store real profile details, competencies, certifications, completed projects, and target career goals.
- Self-rate skills (1–5 stars) with instant composite recalculation.

### 2. Skill Analysis & Career Matching
- Real-time comparison between current learner skills and chosen role benchmarks:
  - **Full Stack Developer**
  - **AI / ML Engineer**
  - **Cloud & DevOps Engineer**
  - **Data Scientist**
- Example: Identifies Python, SQL, and HTML $\rightarrow$ highlights missing competencies: **JavaScript**, **React**, and **Node.js**.

### 3. Learning Recommendations & Visual DAG
- Interactive SVG dependency graph.
- **Dependency Unlock Path**: Locks advanced topics until prerequisites are mastered.
- Transparent *"Why this pick?"* explanations for every course and practical exercise.

### 4. Progress Tracking & Confidence Meter
- Tracks real lessons, assessments, streaks, and milestone completions.
- **Confidence Meter**: Detects **Dunning-Kruger Risk** (over-confidence) and **Imposter Syndrome** (under-confidence).

### 5. AI Mentor (Ada) & Weekly Diagnostic
- Interactive guidance tailored to learner gaps.
- **Weekly Check-in**: Diagnostic questions adjust weekly study budget and learning velocity.
- **Explain-Back Mode (Feynman Technique)**: Learner teaches a concept in their own words; the agent grades conceptual depth, clarity, and flags misconceptions.

### 6. Personalized Tests & Live Code Sandbox
- **Adaptive IRT Tests**: Difficulty ($\theta$) dynamically adapts after each attempt based on learning rate. Slower learners receive smaller step sizes and scaffolding hints; fast learners receive harder synthesis questions.
- **Micro-Quizzes in Code**: In-editor challenges pop up directly inside code comments.
- **Live Code Sandbox**: In-browser Python 3 and JavaScript execution environment with unit test assertion reporting.

### 7. Personalized Mock Interview Agent
- Role-specific technical & behavioral interview scenarios.
- Scored evaluations across **Technical Depth**, **Clarity**, **Problem Solving**, and **Communication**.

### 8. Career Pivot Simulator & Roadmap Diff
- Simulates changing career targets.
- Shows transferred skill efficiency, newly required skills, and timeline adjustments.

### 9. Learning Twin & Skill Decay
- **Learning Twin**: Profile mirroring velocity (XP/day), retention curve, and peak focus hours.
- **Ebbinghaus Forgetting Curve**: Models retention decay ($R = e^{-\lambda t}$); triggers 2-minute refresher reminders before retention dips below 75%.

### 10. Cohort & Academic Features
- **Skill Passport**: Cryptographically signed public credential link with SHA-256 digest.
- **Auto-Built Portfolio**: Showcases real completed projects with GitHub links and deploy URLs.
- **Cohort Heatmap**: Academic/university matrix highlighting collective team blindspots.
- **Time-Budget Scheduling**: Automatically soft-pedals study hours during exam weeks or work crunch sprints.

---

## 🔒 Token Vault & Generic Connector Framework

- **AES-256-GCM Encryption**: All access and refresh tokens encrypted with a 96-bit unique nonce and NIST SP 800-38D tag.
- **Unique Data Key Per User**: Derived via PBKDF2-HMAC-SHA256 from the master KMS key and user salt.
- **Zero Token Leakage**: Tokens are **never sent to the browser** and are intercepted by server log scrubbers (`[REDACTED_BY_TOKEN_VAULT]`).
- **Generic Connectors**: New providers are added via JSON files—zero code modifications required.
- **Personal Access Tokens (PAT)** and **Manual CSV/PDF Import** supported.
- **Instant Revocation**: Disconnecting an account revokes access at the provider and purges the key from the vault.

---

## 🚀 Quickstart & Setup

### 1. Launch the Server
```bash
# Option A: Directly with Python
python3 server.py 8000

# Option B: With npm
npm start
```

### 2. Access the Application
Open your browser to:
```
http://localhost:8000
```

### 3. Run Automated Tests
```bash
# Option A: Directly with Python
python3 -m unittest discover -s tests -p "test_*.py"

# Option B: With npm
npm test
```

Expected output:
```
Ran 9 tests in 0.050s

OK
```

---

## 📄 License

This project is licensed under the terms of the [MIT License](LICENSE).
