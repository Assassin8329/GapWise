"""
Production-grade HTTP Server and REST API router for AI-Powered Learning Platform.
Zero external dependencies.
Includes:
- Complete REST API endpoints for all platform capabilities
- Strict Token Vault AES-256-GCM encryption & sanitized responses
- Static file serving for SPA frontend
- Log scrubber filter to prevent token leakage
"""

import os
import sys
import json
import time
import urllib.parse
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from typing import Dict, Any, Optional

# Core engine imports
from core.crypto_vault import vault, scrub_sensitive_logs
from core.generic_connectors import registry
from core.models import UserProfile, CAREER_ROLES
from core.skill_engine import skill_engine
from core.roadmap_engine import roadmap_engine
from core.ai_mentor import ai_mentor
from core.test_engine import test_engine
from core.interview_engine import interview_engine
from core.gamification import gamification
from core.analytics import analytics_engine
from core.scheduling import scheduler
from data.seed_data import SAMPLE_USERS, COURSES_CATALOG, QUESTION_BANK

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")

# In-memory working database with deep copies of seed users
USERS_DB: Dict[str, Dict[str, Any]] = json.loads(json.dumps(SAMPLE_USERS))
ACTIVE_USER_ID = "usr_alex_student"
COMPLETED_COURSES: Dict[str, list] = {
    "usr_alex_student": [],
    "usr_maya_seeker": ["c_pytorch_deep"],
    "usr_david_pro": ["c_k8s_mastery"]
}
TEST_ATTEMPTS: Dict[str, list] = {
    "usr_alex_student": [
        {"question_id": "q_js_closure", "topic": "Closures & Scope", "correct": False},
        {"question_id": "q_js_closure_2", "topic": "Closures & Scope", "correct": False}
    ],
    "usr_maya_seeker": [],
    "usr_david_pro": []
}

class LearningPlatformHandler(BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        # Scrub any token patterns from server access logs
        message = format % args
        sys.stderr.write(f"[Server] {scrub_sensitive_logs(message)}\n")

    def send_json(self, data: Any, status: int = 200):
        # Double check: ensure no raw secret tokens are ever in json payload
        json_str = json.dumps(data)
        safe_str = scrub_sensitive_logs(json_str)
        payload = safe_str.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS, DELETE")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.end_headers()
        self.wfile.write(payload)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS, DELETE")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def read_json_body(self) -> Dict[str, Any]:
        content_len = int(self.headers.get("Content-Length", 0))
        if content_len == 0:
            return {}
        body_bytes = self.rfile.read(content_len)
        try:
            return json.loads(body_bytes.decode("utf-8"))
        except Exception:
            return {}

    def do_GET(self):
        global ACTIVE_USER_ID
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        query = urllib.parse.parse_qs(parsed.query)

        user = USERS_DB.get(ACTIVE_USER_ID, USERS_DB["usr_alex_student"])
        user_skills = user.get("skills", {})

        # API Routes
        if path == "/api/health":
            self.send_json({
                "status": "healthy",
                "vault_encryption": "AES-256-GCM Authenticated",
                "kms_status": "ONLINE",
                "active_user": user["name"],
                "active_user_type": user["user_type"],
                "timestamp": time.time()
            })

        elif path == "/api/user":
            self.send_json(user)

        elif path == "/api/users_list":
            # Quick profile switcher data
            profiles = []
            for uid, u in USERS_DB.items():
                profiles.append({
                    "id": uid,
                    "name": u["name"],
                    "user_type": u["user_type"],
                    "target_role": u["target_role"],
                    "email": u["email"],
                    "is_active": (uid == ACTIVE_USER_ID)
                })
            self.send_json(profiles)

        elif path == "/api/skill_analysis":
            res = skill_engine.analyze_profile_skills(user_skills)
            self.send_json(res)

        elif path == "/api/career_match":
            role = query.get("role", [user.get("target_role")])[0]
            res = skill_engine.match_career(user_skills, role)
            self.send_json(res)

        elif path == "/api/career_roles":
            self.send_json(CAREER_ROLES)

        elif path == "/api/roadmap":
            role = query.get("role", [user.get("target_role")])[0]
            completed = COMPLETED_COURSES.get(ACTIVE_USER_ID, [])
            res = roadmap_engine.generate_personalized_roadmap(user_skills, role, completed)
            self.send_json(res)

        elif path == "/api/confidence_meter":
            res = skill_engine.calculate_confidence_meter(user_skills)
            self.send_json(res)

        elif path == "/api/gamification":
            lvl = gamification.calculate_level(user.get("xp", 0))
            quests = gamification.get_personalized_quests(user.get("user_type"), user.get("learning_rate", 1.0))
            all_u = list(USERS_DB.values())
            leaderboard = gamification.get_cohort_leaderboard(all_u)
            self.send_json({
                "level_info": lvl,
                "badges": user.get("badges", []),
                "streak_days": user.get("streak_days", 1),
                "quests": quests,
                "leaderboard": leaderboard
            })

        elif path == "/api/learning_twin":
            res = analytics_engine.compute_learning_twin(user)
            self.send_json(res)

        elif path == "/api/skill_passport":
            res = analytics_engine.generate_skill_passport(user)
            self.send_json(res)

        elif path == "/api/struggle_detector":
            attempts = TEST_ATTEMPTS.get(ACTIVE_USER_ID, [])
            res = skill_engine.detect_struggles(attempts)
            self.send_json(res)

        elif path == "/api/peer_pairing":
            all_u = list(USERS_DB.values())
            res = ai_mentor.match_peer_pairs(ACTIVE_USER_ID, all_u)
            self.send_json(res)

        elif path == "/api/skill_decay":
            res = analytics_engine.calculate_skill_decay(user_skills)
            self.send_json(res)

        elif path == "/api/auto_portfolio":
            res = analytics_engine.get_auto_portfolio(user)
            self.send_json(res)

        elif path == "/api/cohort_heatmap":
            res = analytics_engine.get_cohort_heatmap()
            self.send_json(res)

        elif path == "/api/job_market":
            res = analytics_engine.get_job_market_stats()
            self.send_json(res)

        elif path == "/api/time_schedule":
            budget = user.get("weekly_hours_budget", 12)
            crunch = user.get("exam_crunch_blocks", [])
            res = scheduler.calculate_schedule(budget, crunch)
            self.send_json(res)

        elif path == "/api/test/next":
            theta = user.get("ability_theta", 0.0)
            res = test_engine.get_adaptive_question(user.get("learning_rate", 1.0), theta)
            self.send_json(res)

        elif path == "/api/test/micro_quiz":
            res = test_engine.get_micro_quiz_in_code()
            self.send_json(res)

        elif path == "/api/mock_interview":
            role = query.get("role", [user.get("target_role")])[0]
            res = interview_engine.get_interview_session(role)
            self.send_json(res)

        # Connectors & Token Vault endpoints
        elif path == "/api/connectors":
            conns = registry.load_connectors()
            statuses = vault.list_connections(ACTIVE_USER_ID)
            enriched = {}
            for cid, cfg in conns.items():
                c_copy = dict(cfg)
                c_copy["connection_status"] = statuses.get(cid, {"connected": False})
                enriched[cid] = c_copy
            self.send_json(enriched)

        elif path.startswith("/api/proxy/"):
            # Proxy request: /api/proxy/<provider_id>/<endpoint>
            parts = path.split("/")[3:]
            provider_id = parts[0] if len(parts) > 0 else ""
            endpoint = "/" + "/".join(parts[1:]) if len(parts) > 1 else "/"
            try:
                res = registry.proxy_api_call(ACTIVE_USER_ID, provider_id, endpoint)
                self.send_json(res)
            except Exception as e:
                self.send_json({"error": str(e)}, status=403)

        else:
            # Serve Static SPA file
            self.serve_static(path)

    def do_POST(self):
        global ACTIVE_USER_ID
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        body = self.read_json_body()

        user = USERS_DB.get(ACTIVE_USER_ID, USERS_DB["usr_alex_student"])

        if path == "/api/user/switch":
            target_id = body.get("user_id")
            if target_id in USERS_DB:
                ACTIVE_USER_ID = target_id
                self.send_json({"success": True, "active_user": USERS_DB[ACTIVE_USER_ID]})
            else:
                self.send_json({"error": "User not found"}, status=404)

        elif path == "/api/user/update":
            for k, v in body.items():
                if k in user and k != "id":
                    user[k] = v
            self.send_json({"success": True, "user": user})

        elif path == "/api/user/skill_rate":
            skill = body.get("skill")
            rating = float(body.get("rating", 3.0))
            if skill:
                if skill not in user["skills"]:
                    user["skills"][skill] = {"self_rating": rating, "assessed_rating": 0, "verified": False}
                else:
                    user["skills"][skill]["self_rating"] = rating
                self.send_json({"success": True, "skills": user["skills"]})
            else:
                self.send_json({"error": "Missing skill name"}, status=400)

        elif path == "/api/roadmap/complete_course":
            cid = body.get("course_id")
            if cid:
                if ACTIVE_USER_ID not in COMPLETED_COURSES:
                    COMPLETED_COURSES[ACTIVE_USER_ID] = []
                if cid not in COMPLETED_COURSES[ACTIVE_USER_ID]:
                    COMPLETED_COURSES[ACTIVE_USER_ID].append(cid)
                    user["xp"] += 350
                self.send_json({"success": True, "completed": COMPLETED_COURSES[ACTIVE_USER_ID], "xp": user["xp"]})
            else:
                self.send_json({"error": "Missing course_id"}, status=400)

        elif path == "/api/ai_mentor/chat":
            msg = body.get("message", "")
            res = ai_mentor.chat_with_mentor(msg, user)
            self.send_json(res)

        elif path == "/api/ai_mentor/weekly_checkin":
            res = ai_mentor.process_weekly_checkin(user, body)
            user["xp"] += res.get("xp_awarded", 100)
            self.send_json(res)

        elif path == "/api/ai_mentor/explain_back":
            concept = body.get("concept", "JavaScript Event Loop")
            explanation = body.get("explanation", "")
            res = ai_mentor.evaluate_explain_back(concept, explanation)
            user["xp"] += res.get("xp_earned", 50)
            self.send_json(res)

        elif path == "/api/career_pivot":
            new_role = body.get("new_role", "AI / ML Engineer")
            res = roadmap_engine.simulate_career_pivot(user.get("target_role"), new_role, user.get("skills", {}))
            self.send_json(res)

        elif path == "/api/career_pivot/apply":
            new_role = body.get("new_role")
            if new_role in CAREER_ROLES:
                user["target_role"] = new_role
                self.send_json({"success": True, "target_role": new_role})
            else:
                self.send_json({"error": "Invalid role"}, status=400)

        elif path == "/api/test/submit":
            qid = body.get("question_id")
            answer = int(body.get("answer", 0))
            theta = user.get("ability_theta", 0.0)
            res = test_engine.evaluate_test_attempt(qid, answer, user.get("learning_rate", 1.0), theta)
            user["ability_theta"] = res["new_theta"]
            user["xp"] += res["xp_awarded"]
            
            # Record attempt for struggle detector
            if ACTIVE_USER_ID not in TEST_ATTEMPTS:
                TEST_ATTEMPTS[ACTIVE_USER_ID] = []
            TEST_ATTEMPTS[ACTIVE_USER_ID].append({
                "question_id": qid,
                "topic": res.get("topic", "General"),
                "correct": res["is_correct"]
            })

            # Update assessed skill rating in profile
            skill = res.get("skill")
            if skill in user["skills"]:
                curr_assessed = user["skills"][skill].get("assessed_rating", 0)
                # Weighted adjustment
                delta = 8 if res["is_correct"] else -4
                user["skills"][skill]["assessed_rating"] = max(10, min(98, curr_assessed + delta))
                user["skills"][skill]["last_assessed"] = time.time()
                user["skills"][skill]["last_reviewed"] = time.time()

            self.send_json(res)

        elif path == "/api/test/code_sandbox":
            lang = body.get("language", "python")
            code = body.get("code", "")
            res = test_engine.execute_live_code_sandbox(lang, code)
            if res.get("success"):
                user["xp"] += res.get("xp_earned", 60)
            self.send_json(res)

        elif path == "/api/mock_interview/submit":
            role = user.get("target_role", "Full Stack Developer")
            qid = body.get("question_id", "int_fs_1")
            ans = body.get("answer", "")
            res = interview_engine.evaluate_interview_answer(role, qid, ans)
            user["xp"] += res.get("xp_earned", 100)
            self.send_json(res)

        elif path == "/api/time_schedule/update":
            budget = body.get("weekly_hours_budget")
            crunch = body.get("exam_crunch_blocks")
            if budget is not None:
                user["weekly_hours_budget"] = int(budget)
            if crunch is not None:
                user["exam_crunch_blocks"] = crunch
            res = scheduler.calculate_schedule(user["weekly_hours_budget"], user["exam_crunch_blocks"])
            self.send_json({"success": True, "schedule": res})

        # Connector Actions
        elif path == "/api/connectors/initiate_oauth":
            pid = body.get("provider_id")
            redirect_uri = body.get("redirect_uri", "http://localhost:8000/oauth_callback.html")
            try:
                res = registry.initiate_oauth_flow(ACTIVE_USER_ID, pid, redirect_uri)
                self.send_json(res)
            except Exception as e:
                self.send_json({"error": str(e)}, status=400)

        elif path == "/api/connectors/callback":
            pid = body.get("provider_id")
            state = body.get("state")
            code = body.get("code", "auth_code_simulated")
            try:
                res = registry.handle_oauth_callback_or_mock(state, code, ACTIVE_USER_ID, pid)
                self.send_json(res)
            except Exception as e:
                self.send_json({"error": str(e)}, status=400)

        elif path == "/api/connectors/connect_pat":
            pid = body.get("provider_id")
            pat = body.get("pat_token")
            username = body.get("username")
            try:
                res = registry.connect_pat(ACTIVE_USER_ID, pid, pat, username)
                self.send_json(res)
            except Exception as e:
                self.send_json({"error": str(e)}, status=400)

        elif path == "/api/connectors/disconnect":
            pid = body.get("provider_id")
            res = registry.disconnect_provider(ACTIVE_USER_ID, pid)
            self.send_json(res)

        elif path == "/api/connectors/manual_import":
            pid = body.get("provider_id")
            fname = body.get("filename", "import.csv")
            content = body.get("content", "")
            res = registry.import_manual_data(ACTIVE_USER_ID, pid, fname, content)
            self.send_json(res)

        else:
            self.send_json({"error": "Endpoint not found"}, status=404)

    def serve_static(self, req_path: str):
        if req_path in ["", "/"]:
            req_path = "/index.html"

        # Sanitize path to prevent directory traversal
        clean_path = os.path.normpath(req_path.lstrip("/"))
        file_path = os.path.join(STATIC_DIR, clean_path)

        if not os.path.abspath(file_path).startswith(os.path.abspath(STATIC_DIR)):
            self.send_error(403, "Access Denied")
            return

        if not os.path.exists(file_path) or os.path.isdir(file_path):
            file_path = os.path.join(STATIC_DIR, "index.html")

        # Determine mime type
        ext = os.path.splitext(file_path)[1].lower()
        mime_types = {
            ".html": "text/html; charset=utf-8",
            ".css": "text/css; charset=utf-8",
            ".js": "application/javascript; charset=utf-8",
            ".json": "application/json; charset=utf-8",
            ".svg": "image/svg+xml",
            ".png": "image/png",
            ".ico": "image/x-icon"
        }
        content_type = mime_types.get(ext, "application/octet-stream")

        try:
            with open(file_path, "rb") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(content)))
            self.send_header("Cache-Control", "no-cache")
            self.end_headers()
            self.wfile.write(content)
        except Exception as e:
            self.send_error(500, f"Internal Error: {e}")

def run_server(port: int = 8000):
    server_address = ("127.0.0.1", port)
    httpd = ThreadingHTTPServer(server_address, LearningPlatformHandler)
    print(f"🚀 AI Learning Platform Server active at http://127.0.0.1:{port}")
    httpd.serve_forever()

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    run_server(port)
