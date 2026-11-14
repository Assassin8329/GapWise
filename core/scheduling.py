"""
Time-Budget Scheduling Engine:
Schedules study around college exams, crunch sprints, and work commitments,
dynamically smoothing weekly hours and milestones.
"""

from typing import Dict, List, Any

class TimeScheduler:

    @staticmethod
    def calculate_schedule(
        weekly_budget_hours: int,
        exam_crunch_blocks: List[Dict[str, Any]],
        remaining_course_hours: int = 46,
        weeks_ahead: int = 8
    ) -> Dict[str, Any]:
        """
        Dynamically distributes learning hours across an 8-week horizon,
        accounting for exam weeks and crunch blocks without causing burnout.
        """
        schedule_timeline = []
        cumulative_hours_done = 0
        hours_needed = remaining_course_hours

        for week_num in range(1, weeks_ahead + 1):
            # Check if this week falls in an exam/crunch block
            crunch_match = next((b for b in exam_crunch_blocks if b.get("start_week") == week_num), None)
            
            if crunch_match:
                reduction = crunch_match.get("reduction_percent", 50) / 100.0
                effective_hours = max(2, int(weekly_budget_hours * (1.0 - reduction)))
                status = "EXAM_CRUNCH_MODE"
                note = f"{crunch_match.get('name')}: Light maintenance review only ({effective_hours}h)"
            else:
                effective_hours = weekly_budget_hours
                status = "STANDARD_SPRINT"
                note = f"Full study velocity ({effective_hours}h focus)"

            hours_this_week = min(effective_hours, max(0, hours_needed - cumulative_hours_done))
            cumulative_hours_done += hours_this_week
            pct_complete = min(100, round((cumulative_hours_done / max(1, hours_needed)) * 100))

            schedule_timeline.append({
                "week": week_num,
                "planned_hours": hours_this_week,
                "base_budget": weekly_budget_hours,
                "status": status,
                "note": note,
                "cumulative_hours": cumulative_hours_done,
                "completion_progress_percent": pct_complete
            })

        weeks_to_completion = next((w["week"] for w in schedule_timeline if w["completion_progress_percent"] >= 100), weeks_ahead + 2)

        return {
            "weekly_base_budget": weekly_budget_hours,
            "total_hours_required": hours_needed,
            "projected_completion_weeks": weeks_to_completion,
            "crunch_blocks_active": len(exam_crunch_blocks),
            "timeline": schedule_timeline
        }

scheduler = TimeScheduler()
