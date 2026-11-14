# GapWise — Domain-Agnostic AI Learning Workspace

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.9+](https://img.shields.io/badge/Python-3.9%2B-brightgreen.svg)](https://www.python.org/)
[![Security: AES--256--GCM](https://img.shields.io/badge/Token%20Vault-AES--256--GCM-success.svg)](core/crypto_vault.py)
[![OAuth: PKCE S256](https://img.shields.io/badge/OAuth%202.0-RFC%207636%20PKCE-blueviolet.svg)](core/generic_connectors.py)

**GapWise** is an intelligent, real-data-driven learning workspace. It adapts to a learner's chosen domain, language or medium, outcome, pace, and learning style. Career navigation is supported, but the product is not limited to coding or job preparation.

---

## 🎯 Goal & Core Philosophy

- **Goal**: Turn a learner-declared direction into measurable practice, evidence, and progress. Adapt when goals or results change.
- **Target Users**: Anyone learning a subject, preparing for an exam, changing careers, building a craft, or practicing communication. Users create an email/password account or complete Google OAuth.
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
│   ├── ai_mentor.py          # Legacy non-agent product calculations
│   ├── ai_agents.py          # Model-backed mentor, assessment, interview, and planning agents
│   ├── ai_providers.py       # Ollama plus online OpenAI-compatible provider adapters
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

### 1. Real Accounts & Progress Sync
- Startup requires a real email/password account or Google OAuth before entering the app.
- Authentication uses PBKDF2 password hashes and HttpOnly session cookies.
- Google OAuth stores the returned Google token only in the encrypted server-side vault so Gmail/progress connections can be synced without exposing tokens to the browser.
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

### 5. Model-backed AI agents
- Startup defaults to local Ollama with `mimo-v2.6:9b` and a 30,720-token context capacity. If a model rejects that capacity, the provider retries lower capacities automatically.
- Offline chat, adaptive questions, assessment grading, mock interviews, weekly planning, and Explain-Back all call the configured model; there is no canned reply fallback.
- Online mode supports OpenAI Responses API and OpenAI-compatible providers such as OpenRouter, Groq, Together, DeepSeek, OpenCode-compatible endpoints, and custom endpoints. API keys remain in process memory and are never stored in SQLite.

### 6. Personalized Tests & Practice Lab
- **Adaptive model-generated tests**: Each question is generated for the authenticated learner and stored only for that learner until submission.
- **Adaptive Practice Lab**: Learners choose any domain, language or medium, and format. The model generates a challenge and evaluates only the response evidence supplied by the learner. It never pretends that code ran or that an external artifact was validated.

### 7. Personalized Interview & Speaking Studio
- Role-, exam-, presentation-, or outcome-specific scenarios.
- Optional browser voice input measures filler words, gaps, and thinking time, then includes those measurements in the AI coaching response.

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

### 3. Configure the model runtime

Install the Python Ollama client and run Ollama locally:

```bash
python3 -m pip install -r requirements.txt
ollama serve
ollama pull mimo-v2.6:9b
```

GapWise asks for the Ollama host, model, and bounded context window at startup. If Ollama is unavailable, the UI reports that error and does not fabricate an answer.

For online mode, select a provider in startup setup, enter the provider's own API key, base URL, and model name. The key is held only by the running server process.

### 4. Enable real Google OAuth (optional)

Create a Google OAuth web application and add the exact callback URL shown below to its authorized redirect URIs:

```bash
export GOOGLE_CLIENT_ID="your-google-client-id.apps.googleusercontent.com"
export GOOGLE_CLIENT_SECRET="your-google-client-secret"
export GOOGLE_REDIRECT_URI="http://127.0.0.1:8000/api/auth/google/callback"
python3 server.py 8000
```

If Google OAuth is not configured, use the real email/password registration in the startup screen. No local demo profile is created.

### 5. Run Automated Tests
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
