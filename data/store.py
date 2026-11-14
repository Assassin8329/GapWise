"""
GapWise Real Data Persistence Store.
Enforces Data Rule:
- Zero fake, seeded, or mock users.
- Stores only real users, real connected tokens in vault, and real assessment attempts.
- Provides empty states when no data is present.
"""

import os
import json
import time
import sqlite3
import hashlib
import hmac
import secrets
from typing import Dict, Any, List, Optional

DB_PATH = os.path.join(os.path.dirname(__file__), "gapwise.db")

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Real users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        avatar_url TEXT,
        user_type TEXT DEFAULT 'student',
        bio TEXT DEFAULT '',
        target_role TEXT DEFAULT '',
        skills_json TEXT DEFAULT '{}',
        certifications_json TEXT DEFAULT '[]',
        projects_json TEXT DEFAULT '[]',
        learning_rate REAL DEFAULT 1.0,
        xp INTEGER DEFAULT 0,
        level INTEGER DEFAULT 1,
        streak_days INTEGER DEFAULT 0,
        badges_json TEXT DEFAULT '[]',
        opt_in_leaderboard INTEGER DEFAULT 1,
        weekly_hours_budget INTEGER DEFAULT 10,
        exam_crunch_json TEXT DEFAULT '[]',
        created_at REAL,
        last_active REAL,
        password_hash TEXT DEFAULT '',
        password_salt TEXT DEFAULT '',
        auth_provider TEXT DEFAULT 'email',
        ability_theta REAL DEFAULT 0,
        goal_domain TEXT DEFAULT '',
        target_outcome TEXT DEFAULT '',
        experience_level TEXT DEFAULT '',
        preferred_learning_style TEXT DEFAULT ''
    )
    """)

    # Authentication columns are additive so existing learner data remains intact.
    cursor.execute("PRAGMA table_info(users)")
    user_columns = {row[1] for row in cursor.fetchall()}
    if "password_hash" not in user_columns:
        cursor.execute("ALTER TABLE users ADD COLUMN password_hash TEXT DEFAULT ''")
    if "password_salt" not in user_columns:
        cursor.execute("ALTER TABLE users ADD COLUMN password_salt TEXT DEFAULT ''")
    if "auth_provider" not in user_columns:
        cursor.execute("ALTER TABLE users ADD COLUMN auth_provider TEXT DEFAULT 'email'")
    if "ability_theta" not in user_columns:
        cursor.execute("ALTER TABLE users ADD COLUMN ability_theta REAL DEFAULT 0")
    if "goal_domain" not in user_columns:
        cursor.execute("ALTER TABLE users ADD COLUMN goal_domain TEXT DEFAULT ''")
    if "target_outcome" not in user_columns:
        cursor.execute("ALTER TABLE users ADD COLUMN target_outcome TEXT DEFAULT ''")
    if "experience_level" not in user_columns:
        cursor.execute("ALTER TABLE users ADD COLUMN experience_level TEXT DEFAULT ''")
    if "preferred_learning_style" not in user_columns:
        cursor.execute("ALTER TABLE users ADD COLUMN preferred_learning_style TEXT DEFAULT ''")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sessions (
        token_hash TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        created_at REAL NOT NULL,
        last_seen REAL NOT NULL,
        expires_at REAL NOT NULL
    )
    """)

    # Real assessment attempts table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS test_attempts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        question_id TEXT NOT NULL,
        topic TEXT NOT NULL,
        is_correct INTEGER NOT NULL,
        xp_awarded INTEGER NOT NULL,
        theta_before REAL,
        theta_after REAL,
        timestamp REAL
    )
    """)

    # Real mock interview history table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS interview_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT NOT NULL,
        target_role TEXT NOT NULL,
        question_id TEXT NOT NULL,
        user_answer TEXT NOT NULL,
        composite_score INTEGER NOT NULL,
        rubric_json TEXT NOT NULL,
        strengths_json TEXT NOT NULL,
        improvements_json TEXT NOT NULL,
        xp_earned INTEGER NOT NULL,
        timestamp REAL
    )
    """)

    # Real completed roadmap courses table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS completed_courses (
        user_id TEXT NOT NULL,
        course_id TEXT NOT NULL,
        completed_at REAL,
        PRIMARY KEY (user_id, course_id)
    )
    """)

    conn.commit()
    conn.close()

init_db()

class DataStore:

    @staticmethod
    def hash_password(password: str, salt: Optional[bytes] = None) -> Dict[str, str]:
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters")
        raw_salt = salt or secrets.token_bytes(16)
        digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), raw_salt, 210_000)
        return {"salt": raw_salt.hex(), "hash": digest.hex()}

    @staticmethod
    def verify_password(password: str, password_hash: str, salt_hex: str) -> bool:
        if not password_hash or not salt_hex:
            return False
        try:
            expected = bytes.fromhex(password_hash)
            salt = bytes.fromhex(salt_hex)
        except ValueError:
            return False
        candidate = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 210_000)
        return hmac.compare_digest(candidate, expected)

    @staticmethod
    def create_session(user_id: str, ttl_seconds: int = 60 * 60 * 24 * 30) -> str:
        token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
        now = time.time()
        conn = sqlite3.connect(DB_PATH)
        conn.execute(
            "INSERT INTO sessions (token_hash, user_id, created_at, last_seen, expires_at) VALUES (?, ?, ?, ?, ?)",
            (token_hash, user_id, now, now, now + ttl_seconds),
        )
        conn.commit()
        conn.close()
        return token

    @staticmethod
    def get_user_by_session(token: str) -> Optional[Dict[str, Any]]:
        if not token:
            return None
        token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
        now = time.time()
        conn = sqlite3.connect(DB_PATH)
        row = conn.execute(
            "SELECT user_id FROM sessions WHERE token_hash = ? AND expires_at > ?",
            (token_hash, now),
        ).fetchone()
        if row:
            conn.execute("UPDATE sessions SET last_seen = ? WHERE token_hash = ?", (now, token_hash))
            conn.commit()
        conn.close()
        return DataStore.get_user(row[0]) if row else None

    @staticmethod
    def revoke_session(token: str) -> None:
        if not token:
            return
        token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
        conn = sqlite3.connect(DB_PATH)
        conn.execute("DELETE FROM sessions WHERE token_hash = ?", (token_hash,))
        conn.commit()
        conn.close()

    @staticmethod
    def get_user(user_id: str) -> Optional[Dict[str, Any]]:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        if not row:
            return None
        return DataStore._row_to_user(row)

    @staticmethod
    def get_user_by_email(email: str) -> Optional[Dict[str, Any]]:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        row = cursor.fetchone()
        conn.close()
        if not row:
            return None
        return DataStore._row_to_user(row)

    @staticmethod
    def list_all_users() -> List[Dict[str, Any]]:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users ORDER BY last_active DESC")
        rows = cursor.fetchall()
        conn.close()
        return [DataStore._row_to_user(r) for r in rows]

    @staticmethod
    def create_or_update_user(user_data: Dict[str, Any]) -> Dict[str, Any]:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        uid = user_data["id"]
        name = user_data.get("name", "Learner")
        email = user_data.get("email", "")
        avatar = user_data.get("avatar_url", "")
        user_type = user_data.get("user_type", "student")
        bio = user_data.get("bio", "")
        target_role = user_data.get("target_role", "")
        skills = json.dumps(user_data.get("skills", {}))
        certs = json.dumps(user_data.get("certifications", []))
        projs = json.dumps(user_data.get("projects", []))
        learning_rate = float(user_data.get("learning_rate", 1.0))
        xp = int(user_data.get("xp", 0))
        level = int(user_data.get("level", 1))
        streak = int(user_data.get("streak_days", 0))
        badges = json.dumps(user_data.get("badges", []))
        opt_in = 1 if user_data.get("opt_in_leaderboard", True) else 0
        budget = int(user_data.get("weekly_hours_budget", 10))
        crunch = json.dumps(user_data.get("exam_crunch_blocks", []))
        password_hash = user_data.get("password_hash", "")
        password_salt = user_data.get("password_salt", "")
        auth_provider = user_data.get("auth_provider", "email")
        ability_theta = float(user_data.get("ability_theta", 0.0))
        goal_domain = user_data.get("goal_domain", "")
        target_outcome = user_data.get("target_outcome", "")
        experience_level = user_data.get("experience_level", "")
        preferred_learning_style = user_data.get("preferred_learning_style", "")
        now = time.time()

        cursor.execute("""
        INSERT INTO users (
            id, name, email, avatar_url, user_type, bio, target_role,
            skills_json, certifications_json, projects_json,
            learning_rate, xp, level, streak_days, badges_json,
            opt_in_leaderboard, weekly_hours_budget, exam_crunch_json,
            created_at, last_active, password_hash, password_salt, auth_provider, ability_theta,
            goal_domain, target_outcome, experience_level, preferred_learning_style
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            name = excluded.name,
            email = excluded.email,
            avatar_url = excluded.avatar_url,
            user_type = excluded.user_type,
            bio = excluded.bio,
            target_role = excluded.target_role,
            skills_json = excluded.skills_json,
            certifications_json = excluded.certifications_json,
            projects_json = excluded.projects_json,
            learning_rate = excluded.learning_rate,
            xp = excluded.xp,
            level = excluded.level,
            streak_days = excluded.streak_days,
            badges_json = excluded.badges_json,
            opt_in_leaderboard = excluded.opt_in_leaderboard,
            weekly_hours_budget = excluded.weekly_hours_budget,
            exam_crunch_json = excluded.exam_crunch_json,
            password_hash = CASE WHEN excluded.password_hash != '' THEN excluded.password_hash ELSE users.password_hash END,
            password_salt = CASE WHEN excluded.password_salt != '' THEN excluded.password_salt ELSE users.password_salt END,
            auth_provider = excluded.auth_provider,
            ability_theta = excluded.ability_theta,
            goal_domain = excluded.goal_domain,
            target_outcome = excluded.target_outcome,
            experience_level = excluded.experience_level,
            preferred_learning_style = excluded.preferred_learning_style,
            last_active = excluded.last_active
        """, (
            uid, name, email, avatar, user_type, bio, target_role,
            skills, certs, projs,
            learning_rate, xp, level, streak, badges,
            opt_in, budget, crunch,
            now, now, password_hash, password_salt, auth_provider, ability_theta,
            goal_domain, target_outcome, experience_level, preferred_learning_style
        ))
        conn.commit()
        conn.close()
        return DataStore.get_user(uid)

    @staticmethod
    def record_test_attempt(
        user_id: str,
        question_id: str,
        topic: str,
        is_correct: bool,
        xp_awarded: int,
        theta_before: float,
        theta_after: float
    ):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO test_attempts (user_id, question_id, topic, is_correct, xp_awarded, theta_before, theta_after, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, question_id, topic, 1 if is_correct else 0, xp_awarded, theta_before, theta_after, time.time()))
        conn.commit()
        conn.close()

    @staticmethod
    def get_user_attempts(user_id: str) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT question_id, topic, is_correct, xp_awarded, timestamp FROM test_attempts WHERE user_id = ? ORDER BY timestamp ASC", (user_id,))
        rows = cursor.fetchall()
        conn.close()
        return [{"question_id": r[0], "topic": r[1], "correct": bool(r[2]), "xp": r[3], "timestamp": r[4]} for r in rows]

    @staticmethod
    def record_interview(user_id: str, target_role: str, question_id: str, answer: str, score: int, rubric: dict, strengths: list, improvements: list, xp: int):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO interview_sessions (user_id, target_role, question_id, user_answer, composite_score, rubric_json, strengths_json, improvements_json, xp_earned, timestamp)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, target_role, question_id, answer, score, json.dumps(rubric), json.dumps(strengths), json.dumps(improvements), xp, time.time()))
        conn.commit()
        conn.close()

    @staticmethod
    def get_user_interviews(user_id: str) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT target_role, question_id, composite_score, rubric_json, strengths_json, improvements_json, xp_earned, timestamp FROM interview_sessions WHERE user_id = ? ORDER BY timestamp DESC", (user_id,))
        rows = cursor.fetchall()
        conn.close()
        return [{
            "target_role": r[0],
            "question_id": r[1],
            "composite_score": r[2],
            "rubric": json.loads(r[3]),
            "strengths": json.loads(r[4]),
            "improvements": json.loads(r[5]),
            "xp_earned": r[6],
            "timestamp": r[7]
        } for r in rows]

    @staticmethod
    def mark_course_completed(user_id: str, course_id: str):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO completed_courses (user_id, course_id, completed_at) VALUES (?, ?, ?)", (user_id, course_id, time.time()))
        conn.commit()
        conn.close()

    @staticmethod
    def get_completed_courses(user_id: str) -> List[str]:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT course_id FROM completed_courses WHERE user_id = ?", (user_id,))
        rows = cursor.fetchall()
        conn.close()
        return [r[0] for r in rows]

    @staticmethod
    def _row_to_user(row) -> Dict[str, Any]:
        return {
            "id": row[0],
            "name": row[1],
            "email": row[2],
            "avatar_url": row[3],
            "user_type": row[4],
            "bio": row[5],
            "target_role": row[6],
            "skills": json.loads(row[7]) if row[7] else {},
            "certifications": json.loads(row[8]) if row[8] else [],
            "projects": json.loads(row[9]) if row[9] else [],
            "learning_rate": row[10],
            "xp": row[11],
            "level": row[12],
            "streak_days": row[13],
            "badges": json.loads(row[14]) if row[14] else [],
            "opt_in_leaderboard": bool(row[15]),
            "weekly_hours_budget": row[16],
            "exam_crunch_blocks": json.loads(row[17]) if row[17] else [],
            "created_at": row[18],
            "last_active": row[19],
            "password_hash": row[20] if len(row) > 20 else "",
            "password_salt": row[21] if len(row) > 21 else "",
            "auth_provider": row[22] if len(row) > 22 else "email",
            "ability_theta": row[23] if len(row) > 23 else 0.0,
            "goal_domain": row[24] if len(row) > 24 else "",
            "target_outcome": row[25] if len(row) > 25 else "",
            "experience_level": row[26] if len(row) > 26 else "",
            "preferred_learning_style": row[27] if len(row) > 27 else ""
        }

store = DataStore()
