"""
Domain models and in-memory/persistent state engine for the AI Learning Platform.
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional
import time
import uuid

@dataclass
class SkillRating:
    name: str
    self_rating: float          # 1 to 5 (or converted to 0-100%)
    assessed_rating: float      # 0 to 100% computed from tests
    verified: bool = False
    last_assessed: Optional[float] = None
    decay_rate: float = 0.05    # Ebbinghaus decay parameter
    last_reviewed: float = field(default_factory=time.time)

@dataclass
class ProjectItem:
    id: str
    title: str
    description: str
    skills: List[str]
    github_url: str = ""
    live_demo_url: str = ""
    completed: bool = False
    architecture: str = "Client-Server"
    verified_badge: bool = False

@dataclass
class CertificationItem:
    id: str
    title: str
    issuer: str
    issue_date: str
    credential_url: str = ""
    verified: bool = False

@dataclass
class UserProfile:
    id: str
    name: str
    email: str
    user_type: str              # "student" | "job_seeker" | "professional"
    bio: str
    target_role: str            # e.g. "Full Stack Developer" or learner-selected direction
    skills: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    certifications: List[Dict[str, Any]] = field(default_factory=list)
    projects: List[Dict[str, Any]] = field(default_factory=list)
    
    # Adaptive learning rate: <1.0 = slower (more practice), >1.0 = faster (harder questions sooner)
    learning_rate: float = 1.0
    
    # Gamification
    xp: int = 450
    level: int = 3
    level_title: str = "Beginner"
    streak_days: int = 9
    badges: List[Dict[str, Any]] = field(default_factory=list)
    opt_in_leaderboard: bool = True
    
    # Schedule & Time Budget
    weekly_hours_budget: int = 12
    exam_crunch_blocks: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

# Pre-defined career role benchmark requirements
CAREER_ROLES = {
    "Full Stack Developer": {
        "title": "Full Stack Developer",
        "description": "Architects modern web applications across frontend UI, server-side APIs, database modeling, and DevOps deployment.",
        "required_skills": {
            "Python": 80,
            "JavaScript": 85,
            "React": 80,
            "Node.js": 75,
            "SQL": 75,
            "REST APIs": 80,
            "Git": 75,
            "Docker": 65,
            "System Design": 60,
            "Testing & CI/CD": 65
        },
        "salary_range": "$95,000 - $145,000",
        "demand_growth": "+22% YoY",
        "top_employers": ["Google", "Stripe", "Vercel", "Shopify", "Datadog"]
    },
    "AI / ML Engineer": {
        "title": "AI / ML Engineer",
        "description": "Builds and deploys scalable machine learning pipelines, LLM fine-tuning, and production inference systems.",
        "required_skills": {
            "Python": 90,
            "PyTorch": 85,
            "Machine Learning": 85,
            "Deep Learning": 80,
            "Transformers / LLMs": 80,
            "SQL": 70,
            "MLOps": 75,
            "Linear Algebra": 75,
            "Data Preprocessing": 80,
            "Docker": 70
        },
        "salary_range": "$125,000 - $185,000",
        "demand_growth": "+38% YoY",
        "top_employers": ["Anthropic", "OpenAI", "Google DeepMind", "Meta", "NVIDIA"]
    },
    "Cloud & DevOps Engineer": {
        "title": "Cloud & DevOps Engineer",
        "description": "Designs resilient cloud infrastructure, automated CI/CD pipelines, container orchestration, and reliability.",
        "required_skills": {
            "Linux": 85,
            "Docker": 85,
            "Kubernetes": 80,
            "Terraform / IaC": 80,
            "AWS / GCP": 85,
            "CI/CD Pipelines": 85,
            "Python / Bash": 75,
            "Observability": 70,
            "Networking & Security": 75,
            "Git": 80
        },
        "salary_range": "$115,000 - $165,000",
        "demand_growth": "+26% YoY",
        "top_employers": ["Amazon Web Services", "Cloudflare", "Netflix", "Datadog", "GitHub"]
    },
    "Data Scientist": {
        "title": "Data Scientist",
        "description": "Extracts predictive insights from massive datasets through statistical modeling, experiment design, and visualization.",
        "required_skills": {
            "Python": 85,
            "SQL": 90,
            "Statistics & Probability": 85,
            "Pandas & NumPy": 85,
            "Data Visualization": 80,
            "Scikit-Learn": 80,
            "A/B Testing": 75,
            "Business Intelligence": 70,
            "Data Storytelling": 75,
            "Git": 70
        },
        "salary_range": "$105,000 - $155,000",
        "demand_growth": "+19% YoY",
        "top_employers": ["Uber", "Airbnb", "Spotify", "Amazon", "Microsoft"]
    }
}
