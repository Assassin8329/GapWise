"""
GapWise Curriculum & Evaluation Definitions.
Zero fake user data. All learner profiles, scores, and attempts are created by real users.
"""

COURSES_CATALOG = [
    {
        "id": "c_js_deep_dive",
        "title": "Modern JavaScript: Execution Context, Event Loop & Closures",
        "category": "JavaScript",
        "provider": "Interactive Labs",
        "duration_hours": 10,
        "difficulty": "Intermediate",
        "prerequisites": ["HTML & CSS"],
        "unlocks": ["c_react_core", "c_node_async"],
        "why_this_pick": "Mastering the JavaScript Event Loop is essential before building React components and Node.js microservices.",
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
        "why_this_pick": "Mandatory tier-1 requirement for Full Stack Developer roles. Targets React proficiency with state synchronization patterns.",
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
        "why_this_pick": "Connects SQL knowledge with modern JavaScript server runtimes, enabling you to build enterprise REST APIs.",
        "skills_targeted": ["Node.js", "REST APIs", "SQL"],
        "modules_count": 7,
        "practical_exercise": "Build a JWT-secured rate-limited REST API with Postgres relational models.",
        "xp_reward": 400
    },
    {
        "id": "c_fullstack_capstone",
        "title": "Full Stack Production Capstone: Microservices, Docker & CI/CD",
        "category": "Full Stack",
        "provider": "GapWise Engineering Labs",
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
        "why_this_pick": "Essential for AI/ML Engineer matching. Bridges PyTorch rating up to production requirements.",
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
        "why_this_pick": "Resolves highest priority gap for Cloud & DevOps Architect. Transitions from single-host Docker to multi-cluster orchestration.",
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
        "why_this_pick": "Required by 91% of modern Cloud Engineering postings. Turns cloud configuration into version-controlled reproducible code.",
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
        "difficulty": 2,
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
        }
    ]
}
