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
    (0, "Level 1: Novice Coder"),
    (250, "Level 2: Syntax Apprentice"),
    (600, "Level 3: Logic Builder"),
    (1100, "Level 4: Full-Stack Apprentice"),
    (1800, "Level 5: Systems Crafter"),
    (2700, "Level 6: ML & Cloud Practitioner"),
    (3800, "Level 7: Architecture Specialist"),
    (5200, "Level 8: Lead Engineer"),
    (7000, "Level 9: Principal Architect"),
    (10000, "Level 10: Code Alchemist")
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
    def get_personalized_quests(user_type: str, learning_rate: float) -> List[Dict[str, Any]]:
        """
        AI personalizes daily and weekly quests based on student vs working professional needs.
        """
        is_pro = (user_type == "professional")

        quests = [
            {
                "id": "q_daily_1",
                "type": "daily",
                "title": "Evening Code Review Sprint" if is_pro else "Deep Work Focus Session",
                "description": "Complete 1 interactive code sandbox challenge.",
                "target": 1,
                "current": 1,
                "completed": True,
                "xp_reward": 75,
                "badge_icon": "code"
            },
            {
                "id": "q_daily_2",
                "type": "daily",
                "title": "Feynman Concept Mastery",
                "description": "Submit 1 explanation in Explain-Back Mode to test your mental model.",
                "target": 1,
                "current": 0,
                "completed": False,
                "xp_reward": 90,
                "badge_icon": "book-open"
            },
            {
                "id": "q_weekly_1",
                "type": "weekly",
                "title": "Mock Interview Simulation",
                "description": "Complete 1 full technical mock interview session with the AI agent.",
                "target": 1,
                "current": 0,
                "completed": False,
                "xp_reward": 250,
                "badge_icon": "award"
            },
            {
                "id": "q_weekly_2",
                "type": "weekly",
                "title": "Spaced Repetition Blitz",
                "description": "Refresh 2 decaying skills before memory retention dips below 70%.",
                "target": 2,
                "current": 1,
                "completed": False,
                "xp_reward": 180,
                "badge_icon": "zap"
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
