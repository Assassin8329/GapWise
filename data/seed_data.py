"""
Rich realistic seed dataset for AI Learning Platform:
- Sample profiles (Student, Job Seeker, Working Professional)
- Full course library with dependency nodes & explanations
- Question bank with IRT difficulty tags
- Mock interview bank
- Cohort dataset
- Job market demand stats
"""

import time

SAMPLE_USERS = {
    "usr_alex_student": {
        "id": "usr_alex_student",
        "name": "Alex Chen",
        "email": "alex.chen@university.edu",
        "user_type": "student",
        "bio": "Senior Computer Science undergraduate preparing for software engineering roles. Strong foundational logic, building web development depth.",
        "target_role": "Full Stack Developer",
        "skills": {
            "Python": {"self_rating": 4.5, "assessed_rating": 84, "verified": True, "last_assessed": time.time() - 86400*2, "decay_rate": 0.03, "last_reviewed": time.time() - 86400*3},
            "SQL": {"self_rating": 4.0, "assessed_rating": 78, "verified": True, "last_assessed": time.time() - 86400*5, "decay_rate": 0.04, "last_reviewed": time.time() - 86400*6},
            "HTML & CSS": {"self_rating": 3.5, "assessed_rating": 65, "verified": False, "last_assessed": time.time() - 86400*12, "decay_rate": 0.08, "last_reviewed": time.time() - 86400*14},
            "JavaScript": {"self_rating": 2.0, "assessed_rating": 32, "verified": False, "last_assessed": time.time() - 86400*20, "decay_rate": 0.12, "last_reviewed": time.time() - 86400*22},
            "React": {"self_rating": 1.5, "assessed_rating": 18, "verified": False, "last_assessed": None, "decay_rate": 0.15, "last_reviewed": time.time() - 86400*30},
            "Node.js": {"self_rating": 1.0, "assessed_rating": 12, "verified": False, "last_assessed": None, "decay_rate": 0.15, "last_reviewed": time.time() - 86400*30},
            "Git": {"self_rating": 4.0, "assessed_rating": 76, "verified": True, "last_assessed": time.time() - 86400*4, "decay_rate": 0.04, "last_reviewed": time.time() - 86400*5},
            "Docker": {"self_rating": 1.5, "assessed_rating": 22, "verified": False, "last_assessed": None, "decay_rate": 0.12, "last_reviewed": time.time() - 86400*30}
        },
        "certifications": [
            {"id": "cert_1", "title": "Data Structures & Algorithms in Python", "issuer": "UC Berkeley Extension", "issue_date": "2025-10-15", "credential_url": "https://credentials.example.edu/cert-9982", "verified": True},
            {"id": "cert_2", "title": "Database Management Essentials", "issuer": "Coursera", "issue_date": "2026-01-20", "credential_url": "https://coursera.org/verify/DB-7721", "verified": True}
        ],
        "projects": [
            {
                "id": "proj_1",
                "title": "Algorithmic Trading Backtester",
                "description": "Historical equity strategy backtester in Python using NumPy and SQLite with risk ratio analytics.",
                "skills": ["Python", "SQL", "Data Analysis"],
                "github_url": "https://github.com/alex-chen/backtester",
                "live_demo_url": "https://backtester-demo.web.app",
                "completed": True,
                "architecture": "Event-Driven CLI Engine",
                "verified_badge": True
            },
            {
                "id": "proj_2",
                "title": "Campus Club Event Manager",
                "description": "Student organization portal with calendar scheduling and RSVP tracking.",
                "skills": ["HTML & CSS", "Python", "SQLite"],
                "github_url": "https://github.com/alex-chen/campus-portal",
                "live_demo_url": "https://campus-events.web.app",
                "completed": True,
                "architecture": "MVC Web Application",
                "verified_badge": True
            }
        ],
        "learning_rate": 1.15,
        "xp": 1420,
        "level": 4,
        "level_title": "Full-Stack Apprentice",
        "streak_days": 12,
        "badges": [
            {"id": "b_python", "name": "Python Virtuoso", "icon": "code", "unlocked_at": "2026-02-01"},
            {"id": "b_streak10", "name": "Relentless Learner", "icon": "flame", "unlocked_at": "2026-02-10"},
            {"id": "b_sql", "name": "Query Master", "icon": "database", "unlocked_at": "2026-02-12"}
        ],
        "opt_in_leaderboard": True,
        "weekly_hours_budget": 14,
        "exam_crunch_blocks": [
            {"name": "Midterm Exam Week", "start_week": 3, "reduction_percent": 60, "notes": "Algorithms & Operating Systems exams"}
        ]
    },
    "usr_maya_seeker": {
        "id": "usr_maya_seeker",
        "name": "Maya Patel",
        "email": "maya.patel@devcareers.io",
        "user_type": "job_seeker",
        "bio": "Career switcher from Business Analytics into AI/ML Engineering. Seeking to master PyTorch, deep neural networks, and production MLOps.",
        "target_role": "AI / ML Engineer",
        "skills": {
            "Python": {"self_rating": 4.5, "assessed_rating": 88, "verified": True, "last_assessed": time.time() - 86400, "decay_rate": 0.02, "last_reviewed": time.time() - 86400*2},
            "SQL": {"self_rating": 5.0, "assessed_rating": 92, "verified": True, "last_assessed": time.time() - 86400*3, "decay_rate": 0.02, "last_reviewed": time.time() - 86400*3},
            "Machine Learning": {"self_rating": 3.5, "assessed_rating": 68, "verified": True, "last_assessed": time.time() - 86400*7, "decay_rate": 0.06, "last_reviewed": time.time() - 86400*7},
            "PyTorch": {"self_rating": 2.5, "assessed_rating": 45, "verified": False, "last_assessed": time.time() - 86400*14, "decay_rate": 0.10, "last_reviewed": time.time() - 86400*16},
            "Deep Learning": {"self_rating": 2.0, "assessed_rating": 38, "verified": False, "last_assessed": time.time() - 86400*25, "decay_rate": 0.12, "last_reviewed": time.time() - 86400*28},
            "MLOps": {"self_rating": 1.5, "assessed_rating": 20, "verified": False, "last_assessed": None, "decay_rate": 0.15, "last_reviewed": time.time() - 86400*30},
            "Transformers / LLMs": {"self_rating": 2.5, "assessed_rating": 40, "verified": False, "last_assessed": None, "decay_rate": 0.12, "last_reviewed": time.time() - 86400*30}
        },
        "certifications": [
            {"id": "cert_3", "title": "Machine Learning Specialization", "issuer": "DeepLearning.AI", "issue_date": "2025-11-10", "credential_url": "https://coursera.org/verify/ML-552", "verified": True}
        ],
        "projects": [
            {
                "id": "proj_3",
                "title": "Customer Churn Prediction Pipeline",
                "description": "End-to-end ML classification model with feature store and SHAP explainability.",
                "skills": ["Python", "Machine Learning", "SQL"],
                "github_url": "https://github.com/maya-patel/churn-predictor",
                "live_demo_url": "https://churn-predictor.streamlit.app",
                "completed": True,
                "architecture": "Batch Inference Pipeline",
                "verified_badge": True
            }
        ],
        "learning_rate": 1.35,
        "xp": 2680,
        "level": 6,
        "level_title": "ML Practitioner",
        "streak_days": 21,
        "badges": [
            {"id": "b_streak20", "name": "Consistency Champion", "icon": "zap", "unlocked_at": "2026-02-05"},
            {"id": "b_feynman", "name": "Explain-Back Scholar", "icon": "award", "unlocked_at": "2026-02-11"}
        ],
        "opt_in_leaderboard": True,
        "weekly_hours_budget": 20,
        "exam_crunch_blocks": []
    },
    "usr_david_pro": {
        "id": "usr_david_pro",
        "name": "David Miller",
        "email": "david.miller@techcorp.com",
        "user_type": "professional",
        "bio": "Senior Backend Developer transitioning to Cloud Architecture & DevOps. Deep system architecture knowledge, leveling up Kubernetes and Terraform.",
        "target_role": "Cloud & DevOps Engineer",
        "skills": {
            "Linux": {"self_rating": 4.5, "assessed_rating": 86, "verified": True, "last_assessed": time.time() - 86400*4, "decay_rate": 0.03, "last_reviewed": time.time() - 86400*4},
            "Docker": {"self_rating": 4.0, "assessed_rating": 80, "verified": True, "last_assessed": time.time() - 86400*6, "decay_rate": 0.04, "last_reviewed": time.time() - 86400*6},
            "Python / Bash": {"self_rating": 4.5, "assessed_rating": 88, "verified": True, "last_assessed": time.time() - 86400*2, "decay_rate": 0.02, "last_reviewed": time.time() - 86400*2},
            "Kubernetes": {"self_rating": 2.5, "assessed_rating": 48, "verified": False, "last_assessed": time.time() - 86400*15, "decay_rate": 0.09, "last_reviewed": time.time() - 86400*18},
            "Terraform / IaC": {"self_rating": 2.0, "assessed_rating": 35, "verified": False, "last_assessed": time.time() - 86400*24, "decay_rate": 0.11, "last_reviewed": time.time() - 86400*26},
            "AWS / GCP": {"self_rating": 3.5, "assessed_rating": 62, "verified": True, "last_assessed": time.time() - 86400*10, "decay_rate": 0.06, "last_reviewed": time.time() - 86400*12},
            "CI/CD Pipelines": {"self_rating": 3.0, "assessed_rating": 58, "verified": False, "last_assessed": time.time() - 86400*14, "decay_rate": 0.07, "last_reviewed": time.time() - 86400*15}
        },
        "certifications": [
            {"id": "cert_4", "title": "AWS Certified Solutions Architect - Associate", "issuer": "Amazon Web Services", "issue_date": "2025-08-15", "credential_url": "https://aws.amazon.com/verify/SAA-8819", "verified": True}
        ],
        "projects": [
            {
                "id": "proj_4",
                "title": "High-Throughput Microservice Gateway",
                "description": "Reverse proxy and rate limiting gateway containerized with multi-stage Docker builds.",
                "skills": ["Linux", "Docker", "Python / Bash"],
                "github_url": "https://github.com/david-miller/gateway-core",
                "live_demo_url": "https://gateway.example.org",
                "completed": True,
                "architecture": "Microservices Cluster",
                "verified_badge": True
            }
        ],
        "learning_rate": 0.90, # Busy professional preferring concise, high-yield practice
        "xp": 3100,
        "level": 7,
        "level_title": "Systems Specialist",
        "streak_days": 7,
        "badges": [
            {"id": "b_linux", "name": "Kernel Commander", "icon": "terminal", "unlocked_at": "2026-01-10"},
            {"id": "b_aws", "name": "Cloud Pioneer", "icon": "cloud", "unlocked_at": "2026-01-28"}
        ],
        "opt_in_leaderboard": False,
        "weekly_hours_budget": 8,
        "exam_crunch_blocks": [
            {"name": "Q1 Release Sprint", "start_week": 2, "reduction_percent": 50, "notes": "Production migration deliverables"}
        ]
    }
}

COURSES_CATALOG = [
    {
        "id": "c_js_deep_dive",
        "title": "Modern JavaScript: Execution Context, Event Loop & Closures",
        "category": "JavaScript",
        "provider": "Platform Interactive Labs",
        "duration_hours": 10,
        "difficulty": "Intermediate",
        "prerequisites": ["HTML & CSS"],
        "unlocks": ["c_react_core", "c_node_async"],
        "why_this_pick": "Bridges the #1 critical gap identified in your profile. Mastering the JavaScript Event Loop is essential before building React components and Node.js microservices.",
        "skills_targeted": ["JavaScript"],
        "modules_count": 6,
        "practical_exercise": "Build an asynchronous task queue with microtask prioritization.",
        "xp_reward": 350
    },
    {
        "id": "c_react_core",
        "title": "Production React: Custom Hooks, Reconciliation & State Architecture",
        "category": "React",
        "provider": "Frontend Masters",
        "duration_hours": 14,
        "difficulty": "Intermediate",
        "prerequisites": ["c_js_deep_dive"],
        "unlocks": ["c_fullstack_capstone"],
        "why_this_pick": "Mandatory tier-1 requirement for Full Stack Developer roles. Targets your missing React proficiency with real-world state synchronization patterns.",
        "skills_targeted": ["React", "JavaScript"],
        "modules_count": 8,
        "practical_exercise": "Develop an interactive collaborative Kanban board with optimistic UI updates.",
        "xp_reward": 450
    },
    {
        "id": "c_node_async",
        "title": "Scalable Backend APIs with Node.js, Express & Prisma",
        "category": "Node.js",
        "provider": "FullStack Open",
        "duration_hours": 12,
        "difficulty": "Intermediate",
        "prerequisites": ["c_js_deep_dive", "SQL"],
        "unlocks": ["c_fullstack_capstone"],
        "why_this_pick": "Connects your existing SQL knowledge with modern JavaScript server runtimes, enabling you to build enterprise REST APIs.",
        "skills_targeted": ["Node.js", "REST APIs", "SQL"],
        "modules_count": 7,
        "practical_exercise": "Build a JWT-secured rate-limited REST API with Postgres relational models.",
        "xp_reward": 400
    },
    {
        "id": "c_fullstack_capstone",
        "title": "Full Stack Production Capstone: Microservices, Docker & CI/CD",
        "category": "Full Stack",
        "provider": "Antigravity Engineering Labs",
        "duration_hours": 20,
        "difficulty": "Advanced",
        "prerequisites": ["c_react_core", "c_node_async"],
        "unlocks": [],
        "why_this_pick": "The capstone project will automatically deploy to your verified Skill Passport and portfolio, proving job-readiness to recruiters.",
        "skills_targeted": ["React", "Node.js", "Docker", "Testing & CI/CD"],
        "modules_count": 10,
        "practical_exercise": "Deploy a multi-tenant cloud SaaS with automated GitHub Actions pipeline.",
        "xp_reward": 600
    },
    {
        "id": "c_pytorch_deep",
        "title": "PyTorch Neural Architecture: From Tensors to Transformers",
        "category": "PyTorch",
        "provider": "DeepLearning.AI",
        "duration_hours": 16,
        "difficulty": "Intermediate",
        "prerequisites": ["Python", "Machine Learning"],
        "unlocks": ["c_mlops_prod"],
        "why_this_pick": "Essential for AI/ML Engineer matching. Bridges your current 45% PyTorch rating up to the target 85% requirement.",
        "skills_targeted": ["PyTorch", "Deep Learning"],
        "modules_count": 8,
        "practical_exercise": "Implement multi-head self-attention from scratch and train a language model.",
        "xp_reward": 500
    },
    {
        "id": "c_mlops_prod",
        "title": "Production MLOps: Model Registry, Drift Detection & KServe",
        "category": "MLOps",
        "provider": "Coursera Enterprise",
        "duration_hours": 15,
        "difficulty": "Advanced",
        "prerequisites": ["c_pytorch_deep", "Docker"],
        "unlocks": [],
        "why_this_pick": "Top differentiator in competitive ML job postings. Demonstrates ability to serve models at scale with continuous monitoring.",
        "skills_targeted": ["MLOps", "Transformers / LLMs", "Docker"],
        "modules_count": 7,
        "practical_exercise": "Deploy a low-latency model inference API with Prometheus telemetry and automated canary rollouts.",
        "xp_reward": 550
    },
    {
        "id": "c_k8s_mastery",
        "title": "Kubernetes in Production: Architecture, CRDs & Service Meshes",
        "category": "Kubernetes",
        "provider": "Linux Foundation",
        "duration_hours": 18,
        "difficulty": "Advanced",
        "prerequisites": ["Linux", "Docker"],
        "unlocks": ["c_terraform_iac"],
        "why_this_pick": "Resolves your highest priority gap for Cloud & DevOps Architect. Transitions you from single-host Docker to enterprise multi-cluster orchestration.",
        "skills_targeted": ["Kubernetes", "Observability"],
        "modules_count": 9,
        "practical_exercise": "Set up a high-availability cluster with ingress controller and mutual TLS.",
        "xp_reward": 550
    },
    {
        "id": "c_terraform_iac",
        "title": "Declarative Cloud Infrastructure with Terraform & OpenTofu",
        "category": "Terraform / IaC",
        "provider": "HashiCorp Certified Track",
        "duration_hours": 14,
        "difficulty": "Intermediate",
        "prerequisites": ["c_k8s_mastery", "AWS / GCP"],
        "unlocks": [],
        "why_this_pick": "Required by 91% of modern Cloud Engineering postings. Turns manual cloud configuration into version-controlled reproducible code.",
        "skills_targeted": ["Terraform / IaC", "CI/CD Pipelines", "AWS / GCP"],
        "modules_count": 6,
        "practical_exercise": "Provision an automated multi-region VPC with automated state locking in S3.",
        "xp_reward": 500
    }
]

QUESTION_BANK = [
    {
        "id": "q_js_event_loop",
        "skill": "JavaScript",
        "topic": "Event Loop & Microtasks",
        "difficulty": 2, # IRT parameter b = 2
        "type": "multiple_choice",
        "question": "What is the exact execution order of the following JavaScript snippet?",
        "code_snippet": "console.log('1');\nsetTimeout(() => console.log('2'), 0);\nPromise.resolve().then(() => console.log('3'));\nconsole.log('4');",
        "options": [
            "1, 4, 3, 2",
            "1, 2, 3, 4",
            "1, 4, 2, 3",
            "1, 3, 4, 2"
        ],
        "correct_answer": 0,
        "explanation": "Synchronous code executes first ('1', '4'). Next, the microtask queue (Promises) resolves ('3'). Finally, macrotask queue (setTimeout) is processed ('2').",
        "hint": "Microtasks (Promises) always run before the next macrotask (setTimeout)."
    },
    {
        "id": "q_js_closure",
        "skill": "JavaScript",
        "topic": "Closures & Scope",
        "difficulty": 3,
        "type": "multiple_choice",
        "question": "In the following snippet, what will the invocation `counter()` return after calling `createCounter(5)`?",
        "code_snippet": "function createCounter(n) {\n  let count = n;\n  return () => ++count;\n}\nconst counter = createCounter(5);\ncounter();\nconsole.log(counter());",
        "options": [
            "7",
            "6",
            "5",
            "NaN"
        ],
        "correct_answer": 0,
        "explanation": "The inner arrow function forms a closure over `count`. First call increments to 6, second call increments and returns 7.",
        "hint": "Each call to counter modifies the enclosed variable in memory."
    },
    {
        "id": "q_react_hooks",
        "skill": "React",
        "topic": "useEffect Dependency Array",
        "difficulty": 3,
        "type": "multiple_choice",
        "question": "Why would an empty dependency array `[]` in a `useEffect` hook cause stale closure bugs when accessing state?",
        "options": [
            "The effect captures state variables at mount time and never re-evaluates them on subsequent renders.",
            "Empty arrays tell React to run the effect on every single re-render cycle.",
            "Empty arrays trigger memory leaks by disabling garbage collection.",
            "React disallows empty arrays in strict mode."
        ],
        "correct_answer": 0,
        "explanation": "With an empty dependency array, the callback closure retains references to variables from the initial render, missing state updates.",
        "hint": "Think about what lexical variables are closed over on initial execution."
    },
    {
        "id": "q_sql_join_perf",
        "skill": "SQL",
        "topic": "Query Optimization & Indexing",
        "difficulty": 4,
        "type": "multiple_choice",
        "question": "When querying 10,000,000 records with `WHERE user_id = 42 AND created_at > '2026-01-01'`, which index layout provides the best seek performance?",
        "options": [
            "Composite B-Tree index on (user_id, created_at)",
            "Composite B-Tree index on (created_at, user_id)",
            "Separate single-column indexes on user_id and created_at",
            "Full-text GIN index on created_at"
        ],
        "correct_answer": 0,
        "explanation": "Equality filters (user_id = 42) must precede range filters (created_at > ...) in composite indexes so the engine can binary-search to the user prefix and scan the range.",
        "hint": "Put equality comparisons before range comparisons in multi-column indexes."
    },
    {
        "id": "q_python_generators",
        "skill": "Python",
        "topic": "Memory Optimization with Generators",
        "difficulty": 3,
        "type": "code_quiz",
        "question": "Fill in the blank to make this stream parser consume constant O(1) memory instead of allocating a list:",
        "code_snippet": "def stream_large_dataset(filepath):\n    with open(filepath, 'r') as f:\n        for line in f:\n            ___ line.strip().split(',')",
        "options": [
            "yield",
            "return",
            "async return",
            "pass"
        ],
        "correct_answer": 0,
        "explanation": "`yield` turns the function into a generator that lazily evaluates lines one by one without buffering the file into RAM.",
        "hint": "What Python keyword yields one element at a time from an iterator?"
    }
]

MOCK_INTERVIEW_BANK = {
    "Full Stack Developer": [
        {
            "id": "int_fs_1",
            "question": "Walk me through what happens under the hood when a user visits a modern Single Page Application (SPA). How does client-side routing, virtual DOM reconciliation, and caching work?",
            "category": "Frontend Architecture",
            "rubric": {
                "technical_depth": "Must explain DNS lookup, initial HTML payload, bundle execution, History API routing, and Virtual DOM diffing algorithm.",
                "clarity": "Logical progression from network to browser render tree.",
                "communication": "Concise delivery without excessive filler words.",
                "problem_solving": "Mentions edge cases like bundle code splitting and SSR/hydration trade-offs."
            },
            "sample_good_answer": "When the user navigates to the URL, DNS resolves the IP, and the browser fetches the shell index.html and compiled JavaScript bundles. Client-side routing intercepts window.location via the HTML5 History API (pushState/popState) without reloading the page. During state updates, React builds a lightweight in-memory Virtual DOM tree, runs the heuristic O(n) diffing reconciliation algorithm against the previous fiber tree, and commits only the minimal dirty batch DOM mutations to the actual document, preserving layout performance."
        },
        {
            "id": "int_fs_2",
            "question": "How would you design an idempotent payment processing API in Node.js and SQL to prevent double-charging users during intermittent network timeouts?",
            "category": "Backend System Design",
            "rubric": {
                "technical_depth": "Idempotency keys, atomic database transactions (SERIALIZABLE or SELECT FOR UPDATE), distributed locking with Redis, status state machines.",
                "clarity": "Step-by-step request lifecycle explanation.",
                "communication": "Structured, authoritative explanation.",
                "problem_solving": "Addresses retry storms and race conditions."
            },
            "sample_good_answer": "I would require clients to submit a unique Idempotency-Key header with every payment POST request. On incoming request, the server acquires a fast distributed lock in Redis for that key. If the key exists in Postgres with status 'COMPLETED', we immediately return the cached response. If 'PROCESSING', we return a 409 Conflict. If new, we insert a pending record inside an ACID database transaction, call the payment gateway with the same idempotency key, update the order status, cache the finalized receipt, and release the lock."
        }
    ],
    "AI / ML Engineer": [
        {
            "id": "int_ml_1",
            "question": "Explain the mechanics of Multi-Head Self-Attention in the Transformer architecture. Why do we scale dot products by the square root of key dimension dk?",
            "category": "Deep Learning Fundamentals",
            "rubric": {
                "technical_depth": "Q, K, V projections, softmax((Q * K^T) / sqrt(d_k)) * V, vanishing gradients explanation for large d_k.",
                "clarity": "Clear matrix dimension and attention head splitting breakdown.",
                "communication": "Mathematical rigor combined with intuitive understanding.",
                "problem_solving": "Addresses computational complexity O(n^2) and memory optimizations."
            },
            "sample_good_answer": "In multi-head attention, input embeddings are projected into Query, Key, and Value vectors across multiple representation subspaces. The scaled dot-product attention computes compatibility between queries and keys. We scale by sqrt(d_k) because for large dimensional vectors, the dot product grows large in magnitude, pushing the softmax function into regions with near-zero gradients (saturation). Dividing by sqrt(d_k) stabilizes the variance back to 1, ensuring robust backpropagation."
        }
    ]
}

COHORT_HEATMAP_DATA = {
    "cohort_name": "Senior CS Batch 2026 - Accelerated Track",
    "skills": ["Python", "JavaScript", "React", "Node.js", "SQL", "Docker", "Git", "System Design"],
    "students": [
        {"name": "Alex Chen", "scores": [84, 32, 18, 12, 78, 22, 76, 45]},
        {"name": "Sophia Zhang", "scores": [72, 85, 88, 70, 65, 50, 82, 60]},
        {"name": "Marcus Vance", "scores": [90, 40, 30, 25, 85, 75, 88, 55]},
        {"name": "Elena Rostova", "scores": [65, 80, 82, 78, 60, 40, 75, 62]},
        {"name": "Jordan Lee", "scores": [88, 92, 90, 85, 82, 70, 90, 78]},
        {"name": "Amina Diop", "scores": [45, 60, 55, 48, 50, 30, 65, 40]},
        {"name": "Liam Murphy", "scores": [78, 70, 65, 60, 75, 58, 80, 65]},
        {"name": "Priya Nair", "scores": [92, 45, 35, 28, 90, 65, 85, 70]},
        {"name": "Carlos Gomez", "scores": [55, 75, 72, 68, 58, 45, 70, 50]},
        {"name": "Hana Tanaka", "scores": [82, 88, 85, 80, 76, 68, 88, 74]}
    ]
}

JOB_MARKET_STATS = [
    {
        "role": "Full Stack Developer",
        "open_positions": "42,850",
        "demand_trend": "+22% YoY",
        "median_salary": "$124,000",
        "top_skills_in_demand": ["React", "TypeScript", "Node.js", "SQL", "Docker", "AWS"],
        "declining_skills": ["jQuery", "PHP (Legacy)", "SOAP APIs"]
    },
    {
        "role": "AI / ML Engineer",
        "open_positions": "28,400",
        "demand_trend": "+38% YoY",
        "median_salary": "$158,000",
        "top_skills_in_demand": ["PyTorch", "LLMs", "RAG Pipelines", "CUDA", "MLOps", "vLLM"],
        "declining_skills": ["Manual Feature Engineering", "Theano"]
    },
    {
        "role": "Cloud & DevOps Engineer",
        "open_positions": "35,120",
        "demand_trend": "+26% YoY",
        "median_salary": "$142,000",
        "top_skills_in_demand": ["Kubernetes", "Terraform", "GitHub Actions", "Prometheus", "eBPF", "AWS/GCP"],
        "declining_skills": ["Manual Server Provisioning", "Chef/Puppet"]
    }
]
