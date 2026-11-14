"""
Roadmap Engine, Dependency Graph DAG, Unlock Path & Career Pivot Simulator.
"""

from typing import Dict, List, Any
from core.models import CAREER_ROLES
from data.seed_data import COURSES_CATALOG

class RoadmapEngine:

    @staticmethod
    def generate_personalized_roadmap(
        user_skills: Dict[str, Dict[str, Any]],
        target_role: str,
        completed_course_ids: List[str] = None
    ) -> Dict[str, Any]:
        """
        Generates a personalized learning roadmap with explicit "Why this pick" reasoning
        and an interactive visual dependency graph (DAG) with locked/unlocked nodes.
        """
        completed = set(completed_course_ids or [])
        role_benchmark = CAREER_ROLES.get(target_role, list(CAREER_ROLES.values())[0])
        required_skills = set(role_benchmark["required_skills"].keys())

        # Filter relevant courses for the target role
        relevant_courses = []
        for course in COURSES_CATALOG:
            course_skills = set(course.get("skills_targeted", []))
            # Match if any course skill overlaps with target role requirements
            if course_skills.intersection(required_skills) or any(skill in course["category"] for skill in required_skills):
                relevant_courses.append(course)

        # Build DAG nodes with unlock status
        nodes = []
        edges = []

        for course in relevant_courses:
            cid = course["id"]
            prereqs = course.get("prerequisites", [])

            # Check if prerequisites are satisfied
            # A prerequisite is met if it's in completed courses OR if the user already has >= 70 in that skill
            prereqs_met = True
            missing_prereqs = []
            for p in prereqs:
                if p in completed:
                    continue
                # If p is a skill name, check user skill rating
                if p in user_skills and user_skills[p].get("assessed_rating", 0) >= 60:
                    continue
                prereqs_met = False
                missing_prereqs.append(p)

            is_completed = cid in completed
            is_unlocked = prereqs_met or is_completed
            status = "COMPLETED" if is_completed else ("UNLOCKED" if is_unlocked else "LOCKED")

            nodes.append({
                "id": cid,
                "title": course["title"],
                "category": course["category"],
                "provider": course["provider"],
                "duration_hours": course["duration_hours"],
                "difficulty": course["difficulty"],
                "why_this_pick": course["why_this_pick"],
                "skills_targeted": course["skills_targeted"],
                "practical_exercise": course["practical_exercise"],
                "xp_reward": course["xp_reward"],
                "prerequisites": prereqs,
                "missing_prerequisites": missing_prereqs,
                "status": status,
                "is_unlocked": is_unlocked,
                "is_completed": is_completed
            })

            # Create edges for visual DAG
            for p in prereqs:
                edges.append({
                    "from": p,
                    "to": cid,
                    "active": is_unlocked
                })

        total_hours = sum(n["duration_hours"] for n in nodes if not n["is_completed"])
        unlocked_count = sum(1 for n in nodes if n["status"] == "UNLOCKED")
        completed_count = sum(1 for n in nodes if n["status"] == "COMPLETED")

        return {
            "target_role": target_role,
            "total_nodes": len(nodes),
            "unlocked_count": unlocked_count,
            "completed_count": completed_count,
            "remaining_hours": total_hours,
            "nodes": nodes,
            "edges": edges
        }

    @staticmethod
    def simulate_career_pivot(
        current_role: str,
        new_role: str,
        user_skills: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Career Pivot Simulator:
        Shows what happens if the learner changes their career goal.
        Produces roadmap diff:
        - Skills Transferred (kept)
        - New Skills to Learn
        - Retired / Non-priority skills
        - Timeline & Difficulty Delta
        """
        curr_benchmark = CAREER_ROLES.get(current_role, list(CAREER_ROLES.values())[0])
        new_benchmark = CAREER_ROLES.get(new_role, list(CAREER_ROLES.values())[1])

        curr_reqs = curr_benchmark["required_skills"]
        new_reqs = new_benchmark["required_skills"]

        transferred_skills = []
        new_skills_needed = []
        retired_skills = []

        # Skills retained / transferred
        for skill, new_target in new_reqs.items():
            if skill in curr_reqs:
                current_user_score = user_skills.get(skill, {}).get("assessed_rating", 0)
                transferred_skills.append({
                    "skill": skill,
                    "target_in_new_role": new_target,
                    "current_score": current_user_score,
                    "transfer_efficiency": "HIGH" if current_user_score >= 60 else "MODERATE"
                })
            else:
                current_user_score = user_skills.get(skill, {}).get("assessed_rating", 0)
                new_skills_needed.append({
                    "skill": skill,
                    "target_in_new_role": new_target,
                    "current_score": current_user_score,
                    "priority": "HIGH"
                })

        # Skills no longer critical
        for skill in curr_reqs:
            if skill not in new_reqs:
                retired_skills.append({
                    "skill": skill,
                    "former_target": curr_reqs[skill]
                })

        overlap_percent = round((len(transferred_skills) / max(1, len(new_reqs))) * 100, 1)

        pivot_viability = "EXCELLENT" if overlap_percent >= 50 else ("GOOD" if overlap_percent >= 30 else "SIGNIFICANT PIVOT")

        return {
            "current_role": current_role,
            "new_role": new_role,
            "overlap_percent": overlap_percent,
            "pivot_viability": pivot_viability,
            "transferred_skills": transferred_skills,
            "new_skills_needed": new_skills_needed,
            "retired_skills": retired_skills,
            "new_salary_range": new_benchmark.get("salary_range"),
            "new_demand_growth": new_benchmark.get("demand_growth")
        }

roadmap_engine = RoadmapEngine()
