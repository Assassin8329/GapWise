"""
Personalized Mock Interview Agent for Target Roles.
Evaluates answers with scored rubrics across Technical Depth, Clarity, Problem-Solving, Communication.
"""

from typing import Dict, List, Any
from data.seed_data import MOCK_INTERVIEW_BANK

class MockInterviewEngine:

    @staticmethod
    def get_interview_session(target_role: str) -> Dict[str, Any]:
        """
        Returns role-specific technical/behavioral interview questions.
        """
        questions = MOCK_INTERVIEW_BANK.get(target_role, [])

        return {
            "target_role": target_role,
            "total_questions": len(questions),
            "questions": questions
        }

    @staticmethod
    def evaluate_interview_answer(
        target_role: str,
        question_id: str,
        user_answer: str,
        audio_duration_seconds: float = 45.0
    ) -> Dict[str, Any]:
        """
        Analyzes the user's spoken or typed answer against role rubric.
        Returns scored feedback, strength points, and areas for improvement.
        """
        answer_text = user_answer.strip()
        word_count = len(answer_text.split())

        # Keywords for technical depth
        tech_keywords = {
            "Full Stack Developer": ["dns", "dom", "virtual dom", "diff", "reconciliation", "bundle", "idempotency", "redis", "transaction", "acid", "react", "state", "cache", "api", "render"],
            "AI / ML Engineer": ["attention", "transformer", "query", "key", "value", "softmax", "gradient", "variance", "dimension", "backprop", "matrix", "weight"]
        }

        role_keywords = tech_keywords.get(target_role, ["system", "architecture", "scale", "performance"])
        matched_keywords = [kw for kw in role_keywords if kw in answer_text.lower()]
        
        # Technical depth score (0-100)
        tech_score = min(98, max(35, int((len(matched_keywords) / max(3, len(role_keywords) * 0.4)) * 85) + (10 if word_count > 40 else 0)))

        # Clarity score (length balance and structure)
        clarity_score = 90 if 40 <= word_count <= 250 else (65 if word_count < 25 else 75)

        # Problem-solving score
        has_edge_cases = any(w in answer_text.lower() for w in ["edge", "trade-off", "performance", "retry", "scale", "timeout", "complexity", "race condition"])
        problem_solving_score = 88 if has_edge_cases else 70

        # Communication score
        communication_score = 85 if word_count >= 30 else 55

        composite_score = round((tech_score * 0.4) + (clarity_score * 0.25) + (problem_solving_score * 0.2) + (communication_score * 0.15))

        # Qualitative constructive feedback
        strengths = []
        improvements = []

        if len(matched_keywords) >= 3:
            strengths.append(f"Strong architectural terminology: clearly incorporated {', '.join(matched_keywords[:3])}.")
        else:
            improvements.append("Incorporate more precise engineering terminology and system mechanics.")

        if has_edge_cases:
            strengths.append("Proactively highlighted operational trade-offs and failure modes.")
        else:
            improvements.append("Discuss edge cases (e.g. concurrency, memory bounds, network partitions).")

        if word_count < 30:
            improvements.append("Answer was too brief for a senior interview. Aim for 2-3 structured minutes (STAR method).")

        return {
            "composite_score": composite_score,
            "rubric_breakdown": {
                "technical_depth": tech_score,
                "clarity": clarity_score,
                "problem_solving": problem_solving_score,
                "communication": communication_score
            },
            "word_count": word_count,
            "strengths": strengths,
            "improvements": improvements,
            "xp_earned": int(composite_score * 1.5)
        }

interview_engine = MockInterviewEngine()
