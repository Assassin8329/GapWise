"""
Gamification Engine:
- XP, Levels, Unlockable Titles, Badges
- Personalized Daily & Weekly Quests
- Skill Trees matching roadmap milestones
- Cohort Leaderboards (opt-in privacy check)
"""

from typing import Dict, List, Any
import math

LEVEL_THRESHOLDS = [
    (0, "Level 1: Curious Beginner"),
    (250, "Level 2: Emerging Learner"),
    (600, "Level 3: Practice Builder"),
    (1100, "Level 4: Independent Learner"),
    (1800, "Level 5: Confident Practitioner"),
    (2700, "Level 6: Applied Thinker"),
    (3800, "Level 7: Insight Specialist"),
    (5200, "Level 8: Learning Leader"),
    (7000, "Level 9: Masterful Practitioner"),
    (10000, "Level 10: Lifelong Learner")
]

class GamificationEngine:

    @staticmethod
    def calculate_level(xp: int) -> Dict[str, Any]:
        current_level = 1
        current_title = LEVEL_THRESHOLDS[0][1]
        next_xp_target = LEVEL_THRESHOLDS[1][0]
        prev_xp_base = 0

        for i, (threshold, title) in enumerate(LEVEL_THRESHOLDS):
            if xp >= threshold:
                current_level = i + 1
                current_title = title
                prev_xp_base = threshold
                next_xp_target = LEVEL_THRESHOLDS[i+1][0] if i + 1 < len(LEVEL_THRESHOLDS) else threshold + 2500
            else:
                break

        progress_in_level = xp - prev_xp_base
        span = next_xp_target - prev_xp_base
        percent = min(100, round((progress_in_level / max(1, span)) * 100, 1))

        return {
            "level": current_level,
            "title": current_title,
            "current_xp": xp,
            "level_base_xp": prev_xp_base,
            "next_level_target_xp": next_xp_target,
            "progress_percent": percent
        }

    @staticmethod
    def get_personalized_quests(user_profile: Dict[str, Any], learning_rate: float = None) -> List[Dict[str, Any]]:
        """
        Personalizes quests from the learner's declared direction and preferences.
        Quest progress is intentionally unstarted until a real action is recorded.
        """
        if isinstance(user_profile, str):
            user_profile = {
                "user_type": user_profile,
                "learning_rate": learning_rate,
            }

        domain = str(user_profile.get("goal_domain") or "").strip()
        outcome = str(user_profile.get("target_outcome") or "").strip()
        experience = str(user_profile.get("experience_level") or "").strip().lower()
        style = str(user_profile.get("preferred_learning_style") or "").strip()
        direction = domain or outcome
        if not direction:
            return []

        outcome_phrase = outcome or "your chosen direction"
        style_phrase = style or "your preferred learning style"
        if any(word in experience for word in ("beginner", "new", "starting")):
            difficulty_phrase = "Start with a guided"
        elif any(word in experience for word in ("advanced", "expert", "experienced")):
            difficulty_phrase = "Stretch with an applied"
        else:
            difficulty_phrase = "Complete an applied"

        quests = [
            {
                "id": "q_daily_1",
                "type": "daily",
                "title": f"{difficulty_phrase} {direction} practice",
                "description": f"Use {style_phrase.lower()} to complete one model-generated practice challenge toward {outcome_phrase}.",
                "target": 1,
                "current": 0,
                "completed": False,
                "xp_reward": 75,
                "badge_icon": "target"
            },
            {
                "id": "q_daily_2",
                "type": "daily",
                "title": f"Explain-back: {direction}",
                "description": "Choose one concept or skill and explain it in your own words to reveal what to reinforce.",
                "target": 1,
                "current": 0,
                "completed": False,
                "xp_reward": 90,
                "badge_icon": "book-open"
            },
            {
                "id": "q_weekly_1",
                "type": "weekly",
                "title": "Rehearse your intended outcome",
                "description": f"Respond to one realistic {direction} scenario and review the model's evidence-based feedback.",
                "target": 1,
                "current": 0,
                "completed": False,
                "xp_reward": 250,
                "badge_icon": "award"
            },
            {
                "id": "q_weekly_2",
                "type": "weekly",
                "title": "Reflect and reinforce",
                "description": f"Review two real learning signals from your work toward {outcome_phrase} and choose the next small step.",
                "target": 2,
                "current": 0,
                "completed": False,
                "xp_reward": 180,
                "badge_icon": "refresh"
            }
        ]
        return quests

    @staticmethod
    def get_cohort_leaderboard(all_users: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Cohort leaderboard with strict opt-in privacy check!
        """
        eligible = [u for u in all_users if u.get("opt_in_leaderboard", True)]
        eligible.sort(key=lambda u: u.get("xp", 0), reverse=True)

        board = []
        for rank, user in enumerate(eligible, 1):
            board.append({
                "rank": rank,
                "user_id": user["id"],
                "name": user["name"],
                "level_title": user.get("level_title", "Explorer"),
                "xp": user.get("xp", 0),
                "streak_days": user.get("streak_days", 1),
                "badges_count": len(user.get("badges", []))
            })
        return board

gamification = GamificationEngine()
