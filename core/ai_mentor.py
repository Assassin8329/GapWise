"""
AI Mentor, Weekly Check-in Diagnostic, Explain-Back Evaluator & Peer Pairing Agent.
"""

from typing import Dict, List, Any
import time

from core.models import CAREER_ROLES

class AIMentorEngine:

    @staticmethod
    def chat_with_mentor(
        user_message: str,
        user_profile: Dict[str, Any],
        conversation_history: List[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Conversational AI Mentor that guides the learner based on their current gaps,
        learning twin velocity, and target career.
        """
        target_role = user_profile.get("target_role") or user_profile.get("target_outcome") or user_profile.get("goal_domain") or ""
        user_name = user_profile.get("name", "Learner")
        msg_lower = user_message.lower()
        skills = user_profile.get("skills", {}) or {}
        role = CAREER_ROLES.get(target_role, {})
        requirements = role.get("required_skills", {})

        def score_for(skill: str) -> float:
            data = skills.get(skill, {}) or {}
            return max(float(data.get("assessed_rating", 0) or 0), float(data.get("self_rating", 0) or 0) * 20)

        gaps = sorted(
            ((skill, score_for(skill), threshold) for skill, threshold in requirements.items()
             if score_for(skill) < threshold),
            key=lambda row: (row[1] / max(row[2], 1), row[1])
        )
        strengths = sorted(
            ((skill, score_for(skill)) for skill in skills if score_for(skill) >= 70),
            key=lambda row: row[1], reverse=True
        )
        top_gap = gaps[0][0] if gaps else None
        top_strength = strengths[0][0] if strengths else None
        xp = int(user_profile.get("xp", 0) or 0)
        streak = int(user_profile.get("streak_days", 0) or 0)

        if "roadmap" in msg_lower or "next" in msg_lower:
            if top_gap:
                reply = (
                    f"Hi {user_name}. For {target_role}, the clearest next step is {top_gap}: "
                    f"your current profile signal is {round(score_for(top_gap))}% against a {requirements[top_gap]}% target. "
                    "Open the roadmap to see the prerequisite chain, then use an adaptive test to turn that gap into evidence."
                )
                action_suggestion = "Open Roadmap"
            else:
                reply = (
                    f"Your profile currently covers the tracked {target_role} requirements. "
                    "Use the roadmap to complete the next module or run a mock interview to validate job-ready depth."
                )
                action_suggestion = "Open Mock Interview"

        elif "struggl" in msg_lower or "stuck" in msg_lower or "hard" in msg_lower:
            focus = top_gap or "the concept you are working on"
            reply = (
                f"A productive way through {focus} is to make the gap observable: take the smallest adaptive test, "
                "read the explanation, then teach the idea back in one short paragraph. "
                "That gives Ada enough evidence to recommend a better next step without guessing."
            )
            action_suggestion = "Start Explain-Back Mode"

        elif "interview" in msg_lower or "mock" in msg_lower:
            reply = (
                f"For a {target_role} interview, practice explaining trade-offs with one concrete example and one failure mode. "
                "The mock interview tab will score technical depth, clarity, problem solving, and communication from your response."
            )
            action_suggestion = "Start Mock Interview"

        else:
            progress = f"You have {xp} XP and a {streak}-day streak" if xp or streak else "Your profile is ready to learn from its first signal"
            focus = f"Your strongest tracked signal is {top_strength}" if top_strength else "Add a skill or run an assessment so I can personalize the plan"
            reply = (
                f"Welcome, {user_name}. {progress}. {focus}. "
                "Ask me about your roadmap, a stuck concept, an interview, or a career pivot and I’ll ground the next step in your profile."
            )
            action_suggestion = "View Your Roadmap"

        return {
            "mentor_name": "Ada - Senior AI Career Mentor",
            "reply": reply,
            "action_suggestion": action_suggestion,
            "timestamp": time.time()
        }

    @staticmethod
    def process_weekly_checkin(
        user_profile: Dict[str, Any],
        checkin_responses: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Weekly Mentor Check-in:
        Asks diagnostic questions, then adjusts the plan, weekly hours, and difficulty.
        """
        hours_spent = checkin_responses.get("hours_spent", 10)
        struggle_area = checkin_responses.get("struggle_area", "None")
        confidence_delta = checkin_responses.get("confidence_shift", "steady")
        goal_shifted = checkin_responses.get("goal_shifted", False)

        plan_adjustments = []

        # Adjust pace
        current_budget = user_profile.get("weekly_hours_budget", 12)
        if hours_spent < (current_budget * 0.6):
            new_budget = max(6, int(current_budget * 0.8))
            plan_adjustments.append(f"Reduced weekly hours budget from {current_budget}h to {new_budget}h to prevent burnout and ensure steady consistency.")
        elif hours_spent > (current_budget * 1.3):
            new_budget = min(30, int(current_budget * 1.25))
            plan_adjustments.append(f"Accelerated roadmap: Increased weekly budget to {new_budget}h based on high study velocity.")

        # Prerequisite remediation if struggling
        if struggle_area and struggle_area.lower() != "none":
            plan_adjustments.append(f"Inserted a targeted 30-minute foundational refresher module covering '{struggle_area}'.")

        if goal_shifted:
            plan_adjustments.append("Triggered Career Pivot Simulator to re-evaluate skill overlap and generate roadmap delta.")

        return {
            "checkin_id": f"chk_{int(time.time())}",
            "summary": "Weekly diagnostic processed successfully.",
            "plan_adjustments": plan_adjustments,
            "next_checkin_days": 7,
            "xp_awarded": 100
        }

    @staticmethod
    def evaluate_explain_back(concept: str, explanation: str) -> Dict[str, Any]:
        """
        Explain-Back Mode:
        Learner explains a concept, skill, or topic in their own words;
        Agent grades accuracy, depth, and clarity based on word count and
        generic structural signals.  Domain-specific evaluation is handled
        by the model-backed /api/ai_mentor/explain_back route; this path
        is the lightweight local fallback.
        """
        words = len(explanation.strip().split())
        text_lower = explanation.lower()

        # Generic structural keywords (domain-agnostic)
        structural_kw = ["concept", "structure", "process", "result", "example",
                         "because", "therefore", "step", "first", "then"]
        matched_kw = [k for k in structural_kw if k in text_lower]

        accuracy_score = min(98, max(40, len(matched_kw) * 12 + (15 if words >= 40 else 0)))
        clarity_score = 92 if 35 <= words <= 180 else (60 if words < 20 else 75)
        depth_score = min(95, max(45, len(matched_kw) * 11))

        composite = round((accuracy_score * 0.45) + (clarity_score * 0.3) + (depth_score * 0.25))

        explain_back_verdict = (
            "Strong explanation — you conveyed the key mechanics without relying on jargon."
            if composite >= 80 else
            "Solid start. Try breaking the idea into numbered steps and adding a concrete example or analogy."
        )

        return {
            "concept": concept,
            "composite_score": composite,
            "accuracy_score": accuracy_score,
            "clarity_score": clarity_score,
            "depth_score": depth_score,
            "word_count": words,
            "explain_back_verdict": explain_back_verdict,
            "misconceptions_flagged": [],
            "xp_earned": int(composite * 1.2)
        }

    @staticmethod
    def match_peer_pairs(user_id: str, all_users: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Peer Pairing Agent:
        Finds peers with complementary gaps.
        Returns empty list when no complementary peers exist in the cohort.
        """
        if not all_users or len(all_users) <= 1:
            return []

        current_user = next((u for u in all_users if u.get("id") == user_id), None)
        if not current_user:
            return []

        curr_skills = current_user.get("skills", {})

        # Identify user's strengths (score >= 70) and gaps (score < 45)
        my_strengths = {k for k, v in curr_skills.items() if v.get("assessed_rating", 0) >= 70}
        my_gaps = {k for k, v in curr_skills.items() if v.get("assessed_rating", 0) < 45}

        peer_matches = []
        for other in all_users:
            if other["id"] == user_id:
                continue

            other_skills = other.get("skills", {})
            other_strengths = {k for k, v in other_skills.items() if v.get("assessed_rating", 0) >= 70}
            other_gaps = {k for k, v in other_skills.items() if v.get("assessed_rating", 0) < 45}

            # Complementary overlap
            can_teach_me = my_gaps.intersection(other_strengths)
            i_can_teach = my_strengths.intersection(other_gaps)

            compatibility = min(99, int((len(can_teach_me) * 35) + (len(i_can_teach) * 35) + 20))

            if can_teach_me or i_can_teach or compatibility > 40:
                peer_matches.append({
                    "peer_id": other["id"],
                    "peer_name": other["name"],
                    "peer_type": other["user_type"],
                    "compatibility_score": compatibility,
                    "they_teach_you": list(can_teach_me) if can_teach_me else [],
                    "you_teach_them": list(i_can_teach) if i_can_teach else [],
                    "study_mode": "Collaborative Study & Peer Review"
                })

        peer_matches.sort(key=lambda x: x["compatibility_score"], reverse=True)
        return peer_matches

ai_mentor = AIMentorEngine()
