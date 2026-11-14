"""Real model-backed GapWise agents.

Every agent delegates to the configured provider. There is deliberately no canned
reply fallback: if the local or online model is unavailable, the API returns an
actionable error and the UI keeps the task in an unstarted state.
"""

import time
import uuid
from typing import Any, Dict, List

from core.ai_providers import AIProviderError, ai_provider_manager


AGENT_SYSTEM = (
    "You are part of GapWise, a career-learning product. Ground every answer in the learner context "
    "and the current conversation. Never invent learner progress, skills, scores, employers, credentials, "
    "or completed work. If evidence is missing, say what evidence is needed. Be concise, specific, and useful."
)


class AIAgentEngine:
    @staticmethod
    def _profile_context(user: Dict[str, Any]) -> str:
        skills = user.get("skills", {}) or {}
        skill_lines = []
        for name, value in skills.items():
            skill_lines.append(
                f"- {name}: self={value.get('self_rating', 0)} / 5, assessed={value.get('assessed_rating', 0)} / 100, "
                f"verified={bool(value.get('verified', False))}"
            )
        return (
            f"Learner name: {user.get('name', 'Learner')}\n"
            f"Growth domain: {user.get('goal_domain') or 'not selected'}\n"
            f"Desired outcome: {user.get('target_outcome') or 'not selected'}\n"
            f"Experience level: {user.get('experience_level') or 'not specified'}\n"
            f"Preferred learning style: {user.get('preferred_learning_style') or 'not specified'}\n"
            f"Target role: {user.get('target_role') or 'not selected'}\n"
            f"XP: {user.get('xp', 0)}\n"
            f"Streak days: {user.get('streak_days', 0)}\n"
            f"Tracked skills:\n{chr(10).join(skill_lines) if skill_lines else '- none yet'}"
        )

    @staticmethod
    def mentor_chat(user: Dict[str, Any], message: str, history: List[Dict[str, str]]) -> Dict[str, Any]:
        messages = [
            {"role": "system", "content": AGENT_SYSTEM + " You are Ada, the GapWise mentor agent.\n\n" + AIAgentEngine._profile_context(user)},
            *history[-12:],
            {"role": "user", "content": message.strip()},
        ]
        reply = ai_provider_manager.chat(messages).strip()
        return {"agent": "ada", "reply": reply, "model": ai_provider_manager.status(), "timestamp": time.time()}

    @staticmethod
    def generate_test(user: Dict[str, Any], attempts: List[Dict[str, Any]]) -> Dict[str, Any]:
        prompt = (
            "Generate one adaptive multiple-choice assessment question for this learner. "
            "Use the tracked skill gaps and prior attempts to choose the next difficulty. "
            "Return JSON only with these keys: question, skill, topic, options (array of 4 strings), "
            "correct_answer (integer 0-3), explanation, hint, difficulty (integer 1-5). "
            "Do not claim the learner knows anything that is not in the context.\n\n"
            f"{AIAgentEngine._profile_context(user)}\n"
            f"Prior attempts: {attempts[-12:] if attempts else 'none'}"
        )
        data = ai_provider_manager.chat_json([
            {"role": "system", "content": AGENT_SYSTEM},
            {"role": "user", "content": prompt},
        ])
        options = data.get("options") or []
        if len(options) != 4 or not isinstance(data.get("correct_answer"), int):
            raise AIProviderError("The test agent returned an incomplete question")
        question_id = f"ai_q_{uuid.uuid4().hex}"
        question = {
            "id": question_id,
            "skill": str(data.get("skill", "General")),
            "topic": str(data.get("topic", "Adaptive assessment")),
            "question": str(data.get("question", "")),
            "options": [str(option) for option in options],
            "correct_answer": max(0, min(3, int(data["correct_answer"]))),
            "explanation": str(data.get("explanation", "")),
            "hint": str(data.get("hint", "")),
            "difficulty": max(1, min(5, int(data.get("difficulty", 2)))),
        }
        return {
            "question": question,
            "target_difficulty": question["difficulty"],
            "current_theta": round(float(user.get("ability_theta", 0.0) or 0.0), 2),
            "show_scaffolding": float(user.get("learning_rate", 1.0) or 1.0) < 1.0,
            "scaffolding_hint": question["hint"],
        }

    @staticmethod
    def evaluate_test(user: Dict[str, Any], question: Dict[str, Any], answer: int) -> Dict[str, Any]:
        prompt = (
            "Evaluate the learner's answer to this generated question. Return JSON only with keys "
            "is_correct (boolean), explanation (string), coaching (string), skill (string), xp_awarded (integer 10-100).\n\n"
            f"Learner context:\n{AIAgentEngine._profile_context(user)}\n"
            f"Question: {question.get('question')}\nOptions: {question.get('options')}\n"
            f"Correct answer index: {question.get('correct_answer')}\nLearner answer index: {answer}\n"
            f"Reference explanation: {question.get('explanation')}"
        )
        data = ai_provider_manager.chat_json([
            {"role": "system", "content": AGENT_SYSTEM + " You are the adaptive assessment evaluator."},
            {"role": "user", "content": prompt},
        ])
        result = {
            "question_id": question["id"],
            "is_correct": bool(data.get("is_correct")),
            "explanation": str(data.get("explanation") or question.get("explanation", "")),
            "coaching": str(data.get("coaching", "")),
            "skill": question.get("skill", "General"),
            "topic": question.get("topic", "Adaptive assessment"),
            "xp_awarded": max(10, min(100, int(data.get("xp_awarded", 10)))),
        }
        return result

    @staticmethod
    def generate_interview(user: Dict[str, Any]) -> Dict[str, Any]:
        direction = user.get("target_role") or user.get("target_outcome") or user.get("goal_domain") or ""
        prompt = (
            "Generate one realistic mock interview question for this learner's declared direction. "
            "Use their growth domain, desired outcome, and target role (whichever are set) to choose the topic. "
            "Return JSON only with keys category, question, follow_up, evaluation_focus. "
            "Do not use a fixed generic question.\n\n"
            + AIAgentEngine._profile_context(user)
        )
        data = ai_provider_manager.chat_json([
            {"role": "system", "content": AGENT_SYSTEM + " You are the GapWise interviewer agent."},
            {"role": "user", "content": prompt},
        ])
        question = {
            "id": f"ai_i_{uuid.uuid4().hex}",
            "category": str(data.get("category", "Role-specific")),
            "question": str(data.get("question", "")),
            "follow_up": str(data.get("follow_up", "")),
            "evaluation_focus": str(data.get("evaluation_focus", "")),
        }
        return {"target_role": direction, "questions": [question], "agent": "interviewer"}

    @staticmethod
    def generate_roadmap(user: Dict[str, Any], completed_course_ids: List[str]) -> Dict[str, Any]:
        prompt = (
            "Create a personalized, domain-agnostic roadmap for this learner. Return JSON only with a nodes array. "
            "Each node must contain id, title, category, description, duration_hours (number), difficulty, why_this_pick, "
            "skills_targeted (array), practical_exercise, instructions (array of concrete steps), evidence, prerequisites (array), "
            "unlocks (array), and xp_reward (integer). Create 3 to 6 nodes. Do not assume the learner is studying software, "
            "do not invent completed work, and do not use generic default curriculum when the domain or outcome is missing. "
            f"Completed evidence IDs: {completed_course_ids or 'none'}\n\n{AIAgentEngine._profile_context(user)}"
        )
        data = ai_provider_manager.chat_json([
            {"role": "system", "content": AGENT_SYSTEM + " You are the roadmap planning agent."},
            {"role": "user", "content": prompt},
        ])
        raw_nodes = data.get("nodes") if isinstance(data, dict) else data
        if not isinstance(raw_nodes, list) or not raw_nodes:
            raise AIProviderError("The roadmap agent returned no steps")
        nodes = []
        for index, raw in enumerate(raw_nodes[:6], start=1):
            if not isinstance(raw, dict) or not raw.get("title"):
                continue
            nodes.append({
                "id": str(raw.get("id") or f"ai_roadmap_{uuid.uuid4().hex}"),
                "title": str(raw.get("title")),
                "category": str(raw.get("category") or "Personalized practice"),
                "description": str(raw.get("description") or ""),
                "duration_hours": max(0.25, min(200, float(raw.get("duration_hours", 1)))),
                "difficulty": str(raw.get("difficulty") or "Adaptive"),
                "why_this_pick": str(raw.get("why_this_pick") or ""),
                "skills_targeted": [str(item) for item in (raw.get("skills_targeted") or [])],
                "practical_exercise": str(raw.get("practical_exercise") or ""),
                "instructions": [str(item) for item in (raw.get("instructions") or [])],
                "evidence": str(raw.get("evidence") or ""),
                "prerequisites": [str(item) for item in (raw.get("prerequisites") or [])],
                "unlocks": [str(item) for item in (raw.get("unlocks") or [])],
                "status": "COMPLETED" if str(raw.get("id")) in completed_course_ids else "UNLOCKED",
                "is_unlocked": True,
                "is_completed": str(raw.get("id")) in completed_course_ids,
                "xp_reward": max(0, min(1000, int(raw.get("xp_reward", 0)))),
            })
        if not nodes:
            raise AIProviderError("The roadmap agent returned incomplete steps")
        return {
            "target_role": user.get("target_outcome") or user.get("target_role") or user.get("goal_domain") or "Personal growth",
            "total_nodes": len(nodes),
            "unlocked_count": sum(1 for node in nodes if node["is_unlocked"]),
            "completed_count": sum(1 for node in nodes if node["is_completed"]),
            "remaining_hours": sum(node["duration_hours"] for node in nodes if not node["is_completed"]),
            "nodes": nodes,
            "edges": [{"from": prerequisite, "to": node["id"], "active": True} for node in nodes for prerequisite in node["prerequisites"]],
            "generated_by": ai_provider_manager.status(),
        }

    @staticmethod
    def generate_practice(user: Dict[str, Any], domain: str, language: str, format_name: str) -> Dict[str, Any]:
        prompt = (
            "Generate one adaptive practice challenge for the learner. Return JSON only with title, domain, language, format, "
            "prompt, instructions (array), success_criteria (array), starter (string), and evaluation_focus (array). "
            "The domain and language/medium must be respected. Language can be a spoken language, programming language, "
            "creative medium, professional method, or any other learner-selected medium. Never pretend to execute code or "
            "validate an external artifact.\n\n"
            f"Chosen domain: {domain}\nChosen language or medium: {language}\nChosen format: {format_name}\n"
            f"{AIAgentEngine._profile_context(user)}"
        )
        data = ai_provider_manager.chat_json([
            {"role": "system", "content": AGENT_SYSTEM + " You are the adaptive practice designer."},
            {"role": "user", "content": prompt},
        ])
        if not data.get("prompt") or not data.get("title"):
            raise AIProviderError("The practice agent returned an incomplete challenge")
        return {
            "id": f"ai_practice_{uuid.uuid4().hex}",
            "title": str(data["title"]),
            "domain": str(data.get("domain") or domain),
            "language": str(data.get("language") or language),
            "format": str(data.get("format") or format_name),
            "prompt": str(data["prompt"]),
            "instructions": [str(item) for item in (data.get("instructions") or [])],
            "success_criteria": [str(item) for item in (data.get("success_criteria") or [])],
            "starter": str(data.get("starter") or ""),
            "evaluation_focus": [str(item) for item in (data.get("evaluation_focus") or [])],
        }

    @staticmethod
    def evaluate_practice(user: Dict[str, Any], challenge: Dict[str, Any], answer: str) -> Dict[str, Any]:
        prompt = (
            "Evaluate the learner response against the supplied challenge. Return JSON only with score (integer 0-100), "
            "verdict, strengths (array), improvements (array), evidence_observed (array), and xp_awarded (integer 0-150). "
            "Be honest: do not claim code ran, a language was fluent, or an artifact was externally validated."
            f"\n\nChallenge: {challenge}\nLearner response:\n{answer}"
        )
        data = ai_provider_manager.chat_json([
            {"role": "system", "content": AGENT_SYSTEM + " You are the practice evaluator."},
            {"role": "user", "content": prompt},
        ])
        return {
            "score": max(0, min(100, int(data.get("score", 0)))),
            "verdict": str(data.get("verdict") or "No verdict returned"),
            "strengths": [str(item) for item in (data.get("strengths") or [])],
            "improvements": [str(item) for item in (data.get("improvements") or [])],
            "evidence_observed": [str(item) for item in (data.get("evidence_observed") or [])],
            "xp_awarded": max(0, min(150, int(data.get("xp_awarded", 0)))),
        }

    @staticmethod
    def evaluate_interview(user: Dict[str, Any], question: Dict[str, Any], answer: str, voice_metrics: Dict[str, Any] = None) -> Dict[str, Any]:
        prompt = (
            "Evaluate this mock interview response. Return JSON only with keys composite_score (integer 0-100), "
            "rubric_breakdown (object with technical_depth, clarity, problem_solving, communication integers), "
            "strengths (array of strings), improvements (array of strings), delivery_feedback (array of strings), xp_earned (integer). "
            "Use only the supplied answer and question.\n\n"
            f"{AIAgentEngine._profile_context(user)}\nQuestion: {question.get('question')}\nAnswer: {answer}\n"
            f"Voice delivery measurements (may be empty): {voice_metrics or {}}"
        )
        data = ai_provider_manager.chat_json([
            {"role": "system", "content": AGENT_SYSTEM + " You are the interview rubric agent."},
            {"role": "user", "content": prompt},
        ])
        rubric = data.get("rubric_breakdown") or {}
        return {
            "composite_score": max(0, min(100, int(data.get("composite_score", 0)))),
            "rubric_breakdown": {key: max(0, min(100, int(rubric.get(key, 0)))) for key in ["technical_depth", "clarity", "problem_solving", "communication"]},
            "strengths": [str(item) for item in (data.get("strengths") or [])],
            "improvements": [str(item) for item in (data.get("improvements") or [])],
            "delivery_feedback": [str(item) for item in (data.get("delivery_feedback") or [])],
            "xp_earned": max(0, min(250, int(data.get("xp_earned", 0)))),
        }

    @staticmethod
    def weekly_checkin(user: Dict[str, Any], checkin: Dict[str, Any]) -> Dict[str, Any]:
        prompt = (
            "Review this learner's weekly check-in and return JSON only with keys: "
            "plan_adjustments (array of concise strings), weekly_hours_budget (integer 1-40), "
            "learning_rate (number 0.5-2.0), focus_reason (string), xp_awarded (integer 0-100). "
            "Use only the supplied check-in and learner context.\n\n"
            f"{AIAgentEngine._profile_context(user)}\n"
            f"Check-in: {checkin}"
        )
        data = ai_provider_manager.chat_json([
            {"role": "system", "content": AGENT_SYSTEM + " You are the weekly planning agent."},
            {"role": "user", "content": prompt},
        ])
        return {
            "plan_adjustments": [str(item) for item in (data.get("plan_adjustments") or [])],
            "weekly_hours_budget": max(1, min(40, int(data.get("weekly_hours_budget", user.get("weekly_hours_budget", 10))))),
            "learning_rate": max(0.5, min(2.0, float(data.get("learning_rate", user.get("learning_rate", 1.0))))),
            "focus_reason": str(data.get("focus_reason", "")),
            "xp_awarded": max(0, min(100, int(data.get("xp_awarded", 0)))),
        }


ai_agents = AIAgentEngine()
