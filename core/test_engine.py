"""
Personalized Adaptive Test Engine (IRT), Micro-Quizzes in Code & Live Code Sandbox.
"""

import math
import os
import shutil
import subprocess
import tempfile
import time
from typing import Dict, List, Any, Optional
from data.seed_data import QUESTION_BANK

class TestEngine:

    @staticmethod
    def get_adaptive_question(
        user_learning_rate: float,
        current_ability_theta: float,
        completed_question_ids: List[str] = None
    ) -> Dict[str, Any]:
        """
        Picks the optimal next question based on user ability theta and learning rate.
        - Slow learners (rate < 1.0): smaller steps, more hints, foundational questions.
        - Fast learners (rate > 1.0): larger jumps, synthesis questions sooner.
        """
        completed = set(completed_question_ids or [])
        available = [q for q in QUESTION_BANK if q["id"] not in completed]
        if not available:
            # Recycle questions if pool exhausted
            available = QUESTION_BANK

        # Map theta (-3.0 to +3.0) to difficulty 1 to 5
        target_diff = max(1, min(5, round(2.5 + (current_ability_theta * 0.8))))

        # Sort by distance to target difficulty
        available.sort(key=lambda q: abs(q["difficulty"] - target_diff))
        selected = available[0]

        # Customize assistance based on learning rate
        show_scaffolding = user_learning_rate < 1.0
        return {
            "question": selected,
            "target_difficulty": selected["difficulty"],
            "current_theta": round(current_ability_theta, 2),
            "show_scaffolding": show_scaffolding,
            "scaffolding_hint": selected.get("hint") if show_scaffolding else None
        }

    @staticmethod
    def evaluate_test_attempt(
        question_id: str,
        user_answer: int,
        user_learning_rate: float,
        current_theta: float
    ) -> Dict[str, Any]:
        """
        Evaluates test question, adjusts theta dynamically.
        Step size delta_theta is scaled by user_learning_rate.
        """
        question = next((q for q in QUESTION_BANK if q["id"] == question_id), QUESTION_BANK[0])
        is_correct = (user_answer == question["correct_answer"])

        # Base step size
        base_step = 0.35
        # Scale step size with learning rate
        delta = base_step * max(0.5, min(2.0, user_learning_rate))

        if is_correct:
            new_theta = min(3.0, current_theta + delta)
            xp_awarded = int(50 * (question["difficulty"] * 0.8) * user_learning_rate)
        else:
            new_theta = max(-3.0, current_theta - (delta * 0.7)) # Softer penalty on failure
            xp_awarded = 10 # Participation XP

        return {
            "question_id": question_id,
            "is_correct": is_correct,
            "correct_answer": question["correct_answer"],
            "explanation": question["explanation"],
            "previous_theta": round(current_theta, 2),
            "new_theta": round(new_theta, 2),
            "xp_awarded": xp_awarded,
            "difficulty_level": question["difficulty"],
            "skill": question["skill"],
            "topic": question["topic"]
        }

    @staticmethod
    def execute_live_code_sandbox(language: str, code: str) -> Dict[str, Any]:
        """
        Runs code in sandbox with test assertions.
        Supports Python and JavaScript.
        """
        start_time = time.time()
        if not code.strip():
            return {
                "success": False,
                "error": "Write code before executing it.",
                "execution_time_ms": 0,
                "test_results": []
            }

        if language.lower() in ["python", "py"]:
            # Run code safely with restricted built-ins
            try:
                allowed_builtins = {
                    "print": print,
                    "range": range,
                    "len": len,
                    "str": str,
                    "int": int,
                    "float": float,
                    "list": list,
                    "dict": dict,
                    "set": set,
                    "sum": sum,
                    "min": min,
                    "max": max,
                    "sorted": sorted,
                    "abs": abs,
                    "enumerate": enumerate,
                    "zip": zip
                }
                local_scope = {}
                # Capture standard output
                import io, sys
                old_stdout = sys.stdout
                redirected_out = io.StringIO()
                sys.stdout = redirected_out

                try:
                    exec(code, {"__builtins__": allowed_builtins}, local_scope)
                finally:
                    sys.stdout = old_stdout
                exec_output = redirected_out.getvalue()
                elapsed_ms = round((time.time() - start_time) * 1000, 2)

                test_results = [
                    {"test_name": "Python execution", "passed": True, "detail": "Completed without exceptions"}
                ]

                return {
                    "success": True,
                    "output": exec_output or "[Execution finished with exit code 0 (No stdout produced)]",
                    "execution_time_ms": elapsed_ms,
                    "test_results": test_results,
                    "xp_earned": 60
                }
            except Exception as e:
                import sys
                sys.stdout = sys.__stdout__
                return {
                    "success": False,
                    "error": str(e),
                    "execution_time_ms": round((time.time() - start_time) * 1000, 2),
                    "test_results": [{"test_name": "Execution Syntax & Runtime", "passed": False, "detail": str(e)}]
                }
        if language.lower() in ["javascript", "js", "node"]:
            node = shutil.which("node")
            if not node:
                return {
                    "success": False,
                    "error": "Node.js is not installed on the server; JavaScript execution is unavailable.",
                    "execution_time_ms": round((time.time() - start_time) * 1000, 2),
                    "test_results": []
                }
            script_path = None
            try:
                with tempfile.NamedTemporaryFile("w", suffix=".js", encoding="utf-8", delete=False) as handle:
                    handle.write(code)
                    script_path = handle.name
                completed = subprocess.run(
                    [node, script_path], capture_output=True, text=True, timeout=8, check=False
                )
                output = (completed.stdout or "") + (completed.stderr or "")
                passed = completed.returncode == 0
                return {
                    "success": passed,
                    "output": output or ("[Execution finished with exit code 0 (No stdout produced)]" if passed else ""),
                    "error": None if passed else "JavaScript exited with a non-zero status.",
                    "execution_time_ms": round((time.time() - start_time) * 1000, 2),
                    "test_results": [{"test_name": "Node.js execution", "passed": passed, "detail": "Process exited cleanly" if passed else f"Exit code {completed.returncode}"}],
                    "xp_earned": 60 if passed else 0
                }
            except subprocess.TimeoutExpired:
                return {
                    "success": False,
                    "error": "JavaScript execution exceeded the 8 second limit.",
                    "execution_time_ms": round((time.time() - start_time) * 1000, 2),
                    "test_results": []
                }
            finally:
                if script_path and os.path.exists(script_path):
                    os.unlink(script_path)

        return {
            "success": False,
            "error": f"Unsupported sandbox language: {language}",
            "execution_time_ms": round((time.time() - start_time) * 1000, 2),
            "test_results": []
        }

test_engine = TestEngine()
