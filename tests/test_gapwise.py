"""
Comprehensive automated test suite for the AI Learning Platform.
"""

import unittest
import os
import secrets
import json
from core.aes_gcm import aes_256_gcm_encrypt, aes_256_gcm_decrypt
from core.crypto_vault import vault, scrub_sensitive_logs, derive_user_data_key
from core.generic_connectors import registry
from core.skill_engine import skill_engine
from core.roadmap_engine import roadmap_engine
from core.test_engine import test_engine
from core.interview_engine import interview_engine
from core.gamification import gamification
from core.analytics import analytics_engine
from core.scheduling import scheduler
from data.seed_data import SAMPLE_USERS

class TestAILearningPlatform(unittest.TestCase):

    def test_01_aes_256_gcm(self):
        """Tests pure-Python AES-256-GCM encryption, decryption, and authentication tag verification."""
        key = secrets.token_bytes(32)
        nonce = secrets.token_bytes(12)
        plaintext = b"super_secret_oauth_refresh_token_xyz"
        aad = b"user_123:github"

        ciphertext_blob = aes_256_gcm_encrypt(key, nonce, plaintext, aad)
        self.assertGreater(len(ciphertext_blob), len(plaintext))

        decrypted = aes_256_gcm_decrypt(key, ciphertext_blob, aad)
        self.assertEqual(decrypted, plaintext)

        # Tamper detection
        tampered = bytearray(ciphertext_blob)
        tampered[-2] ^= 0x55
        with self.assertRaises(ValueError):
            aes_256_gcm_decrypt(key, bytes(tampered), aad)

    def test_02_token_vault_security(self):
        """Verifies Token Vault isolation, encryption, and zero raw token leakage."""
        user_id = "test_usr_8819"
        provider = "github"
        access_tok = "gho_test_1234567890abcdef"
        refresh_tok = "ghr_refresh_0987654321fedcba"

        status = vault.store_token(
            user_id=user_id,
            provider_id=provider,
            access_token=access_tok,
            refresh_token=refresh_tok,
            scopes=["repo:status"]
        )

        # Ensure raw token is NEVER present in the public status
        self.assertNotIn(access_tok, json.dumps(status))
        self.assertNotIn(refresh_tok, json.dumps(status))
        self.assertTrue(status["connected"])
        self.assertEqual(status["masked_token"], "gho_***cdef")

        # Ensure server-side proxy can securely decrypt token internally
        retrieved = vault.retrieve_token(user_id, provider)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved["access_token"], access_tok)

        # Log scrubber test
        log_sample = f"User authenticated with access_token: {access_tok} and Bearer {refresh_tok}"
        scrubbed = scrub_sensitive_logs(log_sample)
        self.assertNotIn(access_tok, scrubbed)
        self.assertIn("[REDACTED_BY_TOKEN_VAULT]", scrubbed)

        # Disconnect test
        revoked = vault.revoke_token(user_id, provider)
        self.assertTrue(revoked)
        self.assertIsNone(vault.retrieve_token(user_id, provider))

    def test_03_generic_connector_framework(self):
        """Verifies JSON connector config loading, PKCE S256 generation, and proxying."""
        connectors = registry.load_connectors()
        self.assertIn("github", connectors)
        self.assertIn("linkedin", connectors)
        self.assertIn("google", connectors)

        # Test PKCE challenge
        pkce = registry.generate_pkce_challenge()
        self.assertIn("code_verifier", pkce)
        self.assertIn("code_challenge", pkce)
        self.assertEqual(pkce["code_challenge_method"], "S256")

        # Test OAuth initiation
        flow = registry.initiate_oauth_flow("usr_test_pkce", "google", "http://localhost:8000/callback")
        self.assertIn("state", flow)
        self.assertIn("auth_url", flow)
        self.assertIn("code_challenge", flow["auth_url"])

    def test_04_skill_engine_analysis_and_matching(self):
        """Verifies skill gap analysis and target career role matching."""
        alex = SAMPLE_USERS["usr_alex_student"]
        analysis = skill_engine.analyze_profile_skills(alex["skills"])
        self.assertGreater(len(analysis["strengths"]), 0)
        self.assertGreater(len(analysis["weaknesses"]), 0)

        # Career match for Full Stack Developer
        match = skill_engine.match_career(alex["skills"], "Full Stack Developer")
        self.assertGreater(match["match_percent"], 20)
        self.assertLess(match["match_percent"], 90) # Alex has gaps in React & Node.js

        # Verify missing skills detected
        missing_names = [m["skill"] for m in match["missing_skills"]]
        self.assertIn("React", missing_names)
        self.assertIn("Node.js", missing_names)

    def test_05_confidence_meter(self):
        """Verifies Confidence Meter detects Dunning-Kruger risk and Imposter Syndrome."""
        test_skills = {
            "SkillA": {"self_rating": 5.0, "assessed_rating": 20.0}, # High self, low assessed => Dunning-Kruger
            "SkillB": {"self_rating": 1.5, "assessed_rating": 90.0}, # Low self, high assessed => Imposter Syndrome
            "SkillC": {"self_rating": 4.0, "assessed_rating": 80.0}  # Calibrated
        }
        meter = skill_engine.calculate_confidence_meter(test_skills)
        flags = {m["skill"]: m["flag"] for m in meter}
        self.assertEqual(flags["SkillA"], "DUNNING_KRUGER_RISK")
        self.assertEqual(flags["SkillB"], "IMPOSTER_SYNDROME")
        self.assertEqual(flags["SkillC"], "CALIBRATED")

    def test_06_roadmap_and_career_pivot(self):
        """Verifies roadmap DAG dependencies, unlock paths, and career pivot diff."""
        alex = SAMPLE_USERS["usr_alex_student"]
        roadmap = roadmap_engine.generate_personalized_roadmap(alex["skills"], "Full Stack Developer", [])
        self.assertGreater(len(roadmap["nodes"]), 0)

        # Verify locked vs unlocked
        nodes_by_id = {n["id"]: n for n in roadmap["nodes"]}
        self.assertTrue(nodes_by_id["c_js_deep_dive"]["is_unlocked"])
        # c_react_core requires c_js_deep_dive
        self.assertFalse(nodes_by_id["c_react_core"]["is_unlocked"])

        # Career pivot simulator
        pivot = roadmap_engine.simulate_career_pivot("Full Stack Developer", "AI / ML Engineer", alex["skills"])
        self.assertGreater(len(pivot["transferred_skills"]), 0)
        self.assertGreater(len(pivot["new_skills_needed"]), 0)
        self.assertIn("overlap_percent", pivot)

    def test_07_adaptive_test_and_sandbox(self):
        """Verifies IRT adaptive testing ability adjustments and live code sandbox."""
        # Fast learner test
        eval_fast = test_engine.evaluate_test_attempt("q_js_event_loop", 0, user_learning_rate=1.5, current_theta=0.0)
        self.assertTrue(eval_fast["is_correct"])
        self.assertGreater(eval_fast["new_theta"], 0.3)

        # Slow learner test
        eval_slow = test_engine.evaluate_test_attempt("q_js_event_loop", 1, user_learning_rate=0.7, current_theta=0.0)
        self.assertFalse(eval_slow["is_correct"])
        self.assertLess(eval_slow["new_theta"], 0.0)

        # Live sandbox test
        py_code = "print('Algorithm test output'); x = sum([10, 20, 30]); print('Sum:', x)"
        sandbox_res = test_engine.execute_live_code_sandbox("python", py_code)
        self.assertTrue(sandbox_res["success"])
        self.assertIn("Sum: 60", sandbox_res["output"])

    def test_08_mock_interview_engine(self):
        """Verifies multi-dimensional mock interview grading."""
        sample_ans = "We implement DNS lookup, virtual DOM diffing algorithm, and ensure idempotency keys in Redis to avoid duplicate transactions."
        eval_res = interview_engine.evaluate_interview_answer("Full Stack Developer", "int_fs_1", sample_ans)
        self.assertGreater(eval_res["composite_score"], 60)
        self.assertIn("technical_depth", eval_res["rubric_breakdown"])
        self.assertIn("clarity", eval_res["rubric_breakdown"])

    def test_09_analytics_and_scheduling(self):
        """Verifies Learning Twin, Skill Passport, and exam-crunch scheduling."""
        alex = SAMPLE_USERS["usr_alex_student"]
        twin = analytics_engine.compute_learning_twin(alex)
        self.assertIn("study_velocity_xp_per_day", twin)

        passport = analytics_engine.generate_skill_passport(alex)
        self.assertIn("signature_hash", passport)
        self.assertIn("shareable_url", passport)

        # Scheduling
        crunch = [{"name": "Midterms", "start_week": 3, "reduction_percent": 60}]
        sched = scheduler.calculate_schedule(weekly_budget_hours=14, exam_crunch_blocks=crunch, remaining_course_hours=40)
        week_3 = next(w for w in sched["timeline"] if w["week"] == 3)
        self.assertEqual(week_3["status"], "EXAM_CRUNCH_MODE")
        self.assertLess(week_3["planned_hours"], 14)

if __name__ == "__main__":
    unittest.main()
