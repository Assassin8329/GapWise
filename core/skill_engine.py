"""
Skill Analysis, Career Matching, Confidence Meter & Struggle Detector Engine.
"""

from typing import Dict, List, Any, Tuple
from core.models import CAREER_ROLES

class SkillEngine:

    @staticmethod
    def analyze_profile_skills(user_skills: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyzes strengths, weaknesses, and verified competency levels.
        """
        strengths = []
        weaknesses = []
        all_skills_analysis = []

        for skill, data in user_skills.items():
            assessed = data.get("assessed_rating", 0) or 0
            self_r = (data.get("self_rating", 1) / 5.0) * 100.0
            composite = (assessed * 0.7) + (self_r * 0.3) if assessed > 0 else self_r

            item = {
                "skill": skill,
                "self_rating_stars": data.get("self_rating", 1),
                "self_rating_percent": round(self_r, 1),
                "assessed_rating": assessed,
                "composite_score": round(composite, 1),
                "verified": data.get("verified", False),
                "last_assessed": data.get("last_assessed")
            }
            all_skills_analysis.append(item)

            if composite >= 75:
                strengths.append(item)
            elif composite < 50:
                weaknesses.append(item)

        strengths.sort(key=lambda x: x["composite_score"], reverse=True)
        weaknesses.sort(key=lambda x: x["composite_score"])

        return {
            "strengths": strengths,
            "weaknesses": weaknesses,
            "all_skills": all_skills_analysis,
            "total_skills_tracked": len(user_skills)
        }

    @staticmethod
    def match_career(user_skills: Dict[str, Dict[str, Any]], target_role_name: str) -> Dict[str, Any]:
        """
        Matches user's current skills against target career role benchmark.
        Shows missing skills, match percentage, and readiness breakdown.
        Example: Python, SQL, basic HTML vs Full Stack Developer => missing JavaScript, React, Node.js.
        """
        role_benchmark = CAREER_ROLES.get(target_role_name)
        if not role_benchmark:
            # Fallback to first available role
            target_role_name = list(CAREER_ROLES.keys())[0]
            role_benchmark = CAREER_ROLES[target_role_name]

        required_skills = role_benchmark["required_skills"]
        matched_skills = []
        missing_skills = []
        partial_skills = []
        
        weighted_score = 0.0
        total_possible = 0.0

        for req_skill, target_score in required_skills.items():
            total_possible += target_score
            user_data = user_skills.get(req_skill)

            if not user_data:
                # Skill is missing completely
                missing_skills.append({
                    "skill": req_skill,
                    "target_score": target_score,
                    "current_score": 0,
                    "gap": target_score,
                    "severity": "CRITICAL" if target_score >= 75 else "IMPORTANT"
                })
            else:
                assessed = user_data.get("assessed_rating", 0) or 0
                self_r = (user_data.get("self_rating", 1) / 5.0) * 100.0
                effective_score = assessed if assessed > 0 else (self_r * 0.7)

                gap = max(0, target_score - effective_score)
                weighted_score += min(effective_score, target_score)

                if gap == 0:
                    matched_skills.append({
                        "skill": req_skill,
                        "target_score": target_score,
                        "current_score": round(effective_score, 1),
                        "status": "READY"
                    })
                elif gap <= 25:
                    partial_skills.append({
                        "skill": req_skill,
                        "target_score": target_score,
                        "current_score": round(effective_score, 1),
                        "gap": round(gap, 1),
                        "status": "NEAR_READY"
                    })
                else:
                    missing_skills.append({
                        "skill": req_skill,
                        "target_score": target_score,
                        "current_score": round(effective_score, 1),
                        "gap": round(gap, 1),
                        "severity": "HIGH_GAP"
                    })

        match_percent = round((weighted_score / total_possible) * 100.0, 1) if total_possible > 0 else 0
        
        # Estimate weeks to career readiness based on missing skill gaps
        total_gap_points = sum(item["gap"] for item in missing_skills) + sum(item["gap"] for item in partial_skills)
        estimated_weeks = max(2, round(total_gap_points / 25))

        return {
            "target_role": target_role_name,
            "description": role_benchmark["description"],
            "match_percent": match_percent,
            "estimated_weeks_to_ready": estimated_weeks,
            "matched_skills": matched_skills,
            "partial_skills": partial_skills,
            "missing_skills": missing_skills,
            "salary_range": role_benchmark.get("salary_range"),
            "demand_growth": role_benchmark.get("demand_growth"),
            "top_employers": role_benchmark.get("top_employers")
        }

    @staticmethod
    def calculate_confidence_meter(user_skills: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Calculates Confidence Meter: Self-Rated vs Assessed Skill.
        Detects Dunning-Kruger (Over-confidence) or Imposter Syndrome (Under-confidence).
        """
        meter_data = []

        for skill, data in user_skills.items():
            assessed = data.get("assessed_rating", 0) or 0
            self_r = (data.get("self_rating", 1) / 5.0) * 100.0

            discrepancy = self_r - assessed

            if assessed == 0:
                flag = "UNTESTED"
                flag_description = "Needs formal assessment test to verify self-rating."
                meter_status = "neutral"
            elif discrepancy > 25:
                flag = "DUNNING_KRUGER_RISK"
                flag_description = f"Over-confidence detected: self-rated at {int(self_r)}% but assessed at {int(assessed)}%."
                meter_status = "warning"
            elif discrepancy < -20:
                flag = "IMPOSTER_SYNDROME"
                flag_description = f"Imposter syndrome detected! You rated yourself at {int(self_r)}%, but your test showed mastery at {int(assessed)}%."
                meter_status = "boost"
            else:
                flag = "CALIBRATED"
                flag_description = f"Well-calibrated: self-perception accurately matches assessed performance."
                meter_status = "success"

            meter_data.append({
                "skill": skill,
                "self_rating": round(self_r, 1),
                "assessed_rating": assessed,
                "discrepancy": round(discrepancy, 1),
                "flag": flag,
                "flag_description": flag_description,
                "meter_status": meter_status
            })

        meter_data.sort(key=lambda x: abs(x["discrepancy"]), reverse=True)
        return meter_data

    @staticmethod
    def detect_struggles(attempt_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Struggle Detector: spots repeated wrong answers across assessments,
        identifies underlying root prerequisite gaps, and recommends remedial micro-lessons.
        """
        concept_misses: Dict[str, int] = {}
        for attempt in attempt_history:
            if not attempt.get("correct", False):
                topic = attempt.get("topic", "General")
                concept_misses[topic] = concept_misses.get(topic, 0) + 1

        struggles = []
        for topic, count in concept_misses.items():
            if count >= 2:
                # Find root prerequisite
                root_cause = "Foundational execution model & scope" if "Closure" in topic or "Event Loop" in topic else "Relational schema indexing & query planning"
                struggles.append({
                    "topic": topic,
                    "repeated_misses": count,
                    "severity": "CRITICAL" if count >= 3 else "MODERATE",
                    "root_prerequisite": root_cause,
                    "remedial_action": f"Recommended 5-minute interactive visualizer on '{topic}' before advancing."
                })

        return {
            "has_struggles": len(struggles) > 0,
            "struggles": struggles
        }

skill_engine = SkillEngine()
