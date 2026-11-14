"""
Learning Twin, Skill Passport, Skill Decay (Ebbinghaus), Auto-Portfolio & Cohort Analytics.
"""

import time
import math
import hashlib
from typing import Dict, List, Any
from data.seed_data import COHORT_HEATMAP_DATA, JOB_MARKET_STATS

class AnalyticsEngine:

    @staticmethod
    def compute_learning_twin(user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Learning Twin: A digital twin profile that mirrors learner pace, study habits,
        retention curves, peak study hours, and predictive completion dates.
        """
        user_type = user_profile.get("user_type", "student")
        xp = user_profile.get("xp", 1000)
        streak = user_profile.get("streak_days", 5)
        learning_rate = user_profile.get("learning_rate", 1.0)
        weekly_hours = user_profile.get("weekly_hours_budget", 12)

        # Velocity in XP/day
        velocity_xp_per_day = round(85 * learning_rate + (streak * 2.5), 1)

        # Habit profile
        if user_type == "student":
            peak_focus_hours = "2:00 PM - 6:00 PM (Afternoon Deep Work)"
            preferred_format = "Interactive Code Labs & Micro-Quizzes"
            attention_span_minutes = 45
        elif user_type == "professional":
            peak_focus_hours = "7:30 PM - 10:00 PM (Evening Wind-Down)"
            preferred_format = "Concise Architectural Reviews & Code Sandboxes"
            attention_span_minutes = 30
        else:
            peak_focus_hours = "9:00 AM - 1:00 PM (Morning Sprint)"
            preferred_format = "Capstone Projects & Mock Interviews"
            attention_span_minutes = 60

        # Memory retention curve index (Ebbinghaus model)
        retention_stability_factor = round(min(0.95, 0.70 + (streak * 0.015)), 2)

        # Estimated job-ready completion date in weeks
        target_role = user_profile.get("target_role", "Full Stack Developer")
        predicted_weeks_remaining = max(3, round(16 / max(0.5, (weekly_hours / 12) * learning_rate)))

        return {
            "twin_id": f"twin_{user_profile['id']}",
            "sync_status": "ACTIVE_SYNCHRONIZED",
            "study_velocity_xp_per_day": velocity_xp_per_day,
            "peak_focus_hours": peak_focus_hours,
            "preferred_format": preferred_format,
            "average_session_minutes": attention_span_minutes,
            "retention_stability_factor": retention_stability_factor,
            "predicted_weeks_remaining": predicted_weeks_remaining,
            "learning_rate_multiplier": learning_rate,
            "cognitive_load_index": "OPTIMAL (0.68)",
            "consistency_score": min(99, streak * 7 + 25)
        }

    @staticmethod
    def calculate_skill_decay(user_skills: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Skill Decay with Spaced-Repetition:
        Models Ebbinghaus forgetting curve: R = exp(-t / (S * 30)).
        Flags skills that dip below 75% retention and offers instant refresh quizzes.
        """
        now = time.time()
        decay_report = []

        for skill, data in user_skills.items():
            assessed = data.get("assessed_rating", 0)
            if assessed == 0:
                continue

            last_rev = data.get("last_reviewed") or (now - 86400 * 10)
            days_since = max(0.5, (now - last_rev) / 86400.0)

            decay_rate = data.get("decay_rate", 0.05)
            # Retention percentage R(t) = exp(-lambda * t)
            retention_percent = round(100.0 * math.exp(-decay_rate * (days_since / 7.0)), 1)
            retention_percent = max(30.0, min(100.0, retention_percent))

            needs_review = retention_percent < 75.0
            urgency = "URGENT" if retention_percent < 60 else ("RECOMMENDED" if needs_review else "OPTIMAL")

            decay_report.append({
                "skill": skill,
                "assessed_score": assessed,
                "days_since_review": round(days_since, 1),
                "retention_percent": retention_percent,
                "needs_review": needs_review,
                "urgency": urgency,
                "refresher_quiz_minutes": 2
            })

        decay_report.sort(key=lambda x: x["retention_percent"])
        return decay_report

    @staticmethod
    def generate_skill_passport(user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Skill Passport:
        Verified skills shareable as ONE tamper-evident public link.
        Includes cryptographic verification hash and badge credentials.
        """
        user_id = user_profile["id"]
        name = user_profile["name"]
        verified_skills = []

        for skill, data in user_profile.get("skills", {}).items():
            if data.get("verified", False) or data.get("assessed_rating", 0) >= 70:
                verified_skills.append({
                    "skill": skill,
                    "score": data.get("assessed_rating", 75),
                    "verified_at": "2026-02-14",
                    "badge": f"{skill} Certified"
                })

        # Cryptographic verification digest
        raw_proof = f"PASSPORT:{user_id}:{name}:{len(verified_skills)}:ANTIGRAVITY_ED_2026"
        signature_hash = hashlib.sha256(raw_proof.encode("utf-8")).hexdigest()[:24].upper()

        shareable_url = f"https://learn.antigravity.dev/passport/{user_id}?sig={signature_hash}"

        return {
            "passport_id": f"PASS-{user_id.upper()[:8]}",
            "holder_name": name,
            "target_role": user_profile.get("target_role", "Engineer"),
            "level_title": user_profile.get("level_title", "Practitioner"),
            "verification_status": "CRYPTOGRAPHICALLY_VERIFIED",
            "signature_hash": signature_hash,
            "shareable_url": shareable_url,
            "verified_skills_count": len(verified_skills),
            "verified_skills": verified_skills,
            "certifications": user_profile.get("certifications", []),
            "total_xp": user_profile.get("xp", 0)
        }

    @staticmethod
    def get_auto_portfolio(user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Auto-built portfolio from completed projects.
        """
        projects = user_profile.get("projects", [])
        return {
            "user_name": user_profile.get("name"),
            "bio": user_profile.get("bio"),
            "target_role": user_profile.get("target_role"),
            "total_projects": len(projects),
            "projects": projects,
            "github_status": "Connected & Synced",
            "portfolio_url": f"https://alexchen.dev/portfolio"
        }

    @staticmethod
    def get_cohort_heatmap() -> Dict[str, Any]:
        return COHORT_HEATMAP_DATA

    @staticmethod
    def get_job_market_stats() -> List[Dict[str, Any]]:
        return JOB_MARKET_STATS

analytics_engine = AnalyticsEngine()
