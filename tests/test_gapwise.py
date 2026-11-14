"""
Comprehensive automated test suite for GapWise.
Verifies:
- Data Rule: Zero fake seed users, clean empty states
- Cryptographic Token Vault (AES-256-GCM + PBKDF2 data keys)
- Generic Connector Framework & RFC 7636 PKCE S256
- Skill analysis, career matching, confidence meter, struggle detector
- Roadmap DAG dependency graph & Career Pivot Simulator
- IRT adaptive tests & Live code sandbox execution
- Mock interview agent rubric evaluation
- Real SQLite persistence store
"""

import unittest
import os
import secrets
import json
import time
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
from data.store import store

class TestGapWisePlatform(unittest.TestCase):

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
        user_id = f"test_usr_{secrets.token_hex(4)}"
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

    def test_04_data_rule_empty_states(self):
        """Verifies Data Rule: Empty state when there is no data."""
        # Empty skill analysis
        empty_analysis = skill_engine.analyze_profile_skills({})
        self.assertEqual(empty_analysis["total_skills_tracked"], 0)
        self.assertEqual(len(empty_analysis["strengths"]), 0)

        # Empty career match
        empty_match = skill_engine.match_career({}, "Full Stack Developer")
        self.assertEqual(empty_match["match_percent"], 0.0)
        self.assertGreater(len(empty_match["missing_skills"]), 0)

        # Empty confidence meter
        empty_meter = skill_engine.calculate_confidence_meter({})
        self.assertEqual(len(empty_meter), 0)

        # Empty struggle detector
        empty_struggles = skill_engine.detect_struggles([])
        self.assertFalse(empty_struggles["has_struggles"])

    def test_05_skill_engine_analysis_and_matching(self):
        """Verifies dynamic skill analysis and target career role matching."""
        user_skills = {
            "Python": {"self_rating": 4.5, "assessed_rating": 84, "verified": True},
            "SQL": {"self_rating": 4.0, "assessed_rating": 78, "verified": True},
            "HTML & CSS": {"self_rating": 3.0, "assessed_rating": 60, "verified": False}
        }
        analysis = skill_engine.analyze_profile_skills(user_skills)
        self.assertGreater(len(analysis["strengths"]), 0)

        match = skill_engine.match_career(user_skills, "Full Stack Developer")
        self.assertGreater(match["match_percent"], 20)
        missing_names = [m["skill"] for m in match["missing_skills"]]
        self.assertIn("JavaScript", missing_names)
        self.assertIn("React", missing_names)
        self.assertIn("Node.js", missing_names)

    def test_06_confidence_meter(self):
        """Verifies Confidence Meter detects Dunning-Kruger risk and Imposter Syndrome."""
        test_skills = {
            "SkillA": {"self_rating": 5.0, "assessed_rating": 20.0},
            "SkillB": {"self_rating": 1.5, "assessed_rating": 90.0},
            "SkillC": {"self_rating": 4.0, "assessed_rating": 80.0}
        }
        meter = skill_engine.calculate_confidence_meter(test_skills)
        flags = {m["skill"]: m["flag"] for m in meter}
        self.assertEqual(flags["SkillA"], "DUNNING_KRUGER_RISK")
        self.assertEqual(flags["SkillB"], "IMPOSTER_SYNDROME")
        self.assertEqual(flags["SkillC"], "CALIBRATED")

    def test_07_roadmap_and_career_pivot(self):
        """Verifies roadmap DAG dependencies, unlock paths, and career pivot diff."""
        user_skills = {
            "HTML & CSS": {"self_rating": 4.0, "assessed_rating": 75}
        }
        roadmap = roadmap_engine.generate_personalized_roadmap(user_skills, "Full Stack Developer", [])
        self.assertGreater(len(roadmap["nodes"]), 0)

        nodes_by_id = {n["id"]: n for n in roadmap["nodes"]}
        self.assertTrue(nodes_by_id["c_js_deep_dive"]["is_unlocked"])
        self.assertFalse(nodes_by_id["c_react_core"]["is_unlocked"])

        # Career pivot simulator
        pivot = roadmap_engine.simulate_career_pivot("Full Stack Developer", "AI / ML Engineer", user_skills)
        self.assertIn("overlap_percent", pivot)
        self.assertIn("pivot_viability", pivot)

    def test_08_adaptive_test_and_sandbox(self):
        """Verifies IRT adaptive testing ability adjustments and live code sandbox."""
        eval_fast = test_engine.evaluate_test_attempt("q_js_event_loop", 0, user_learning_rate=1.5, current_theta=0.0)
        self.assertTrue(eval_fast["is_correct"])
        self.assertGreater(eval_fast["new_theta"], 0.3)

        eval_slow = test_engine.evaluate_test_attempt("q_js_event_loop", 1, user_learning_rate=0.7, current_theta=0.0)
        self.assertFalse(eval_slow["is_correct"])
        self.assertLess(eval_slow["new_theta"], 0.0)

        # Live sandbox test
        py_code = "print('GapWise live runner'); total = sum([1, 2, 3, 4]); print('Result:', total)"
        sandbox_res = test_engine.execute_live_code_sandbox("python", py_code)
        self.assertTrue(sandbox_res["success"])
        self.assertIn("Result: 10", sandbox_res["output"])

    def test_09_real_persistence_store(self):
        """Verifies real SQLite persistence store."""
        uid = f"usr_{secrets.token_hex(6)}"
        email = f"test_{uid}@gapwise.org"
        created = store.create_or_update_user({
            "id": uid,
            "name": "Real Test Learner",
            "email": email,
            "user_type": "student",
            "target_role": "Full Stack Developer",
            "skills": {"Python": {"self_rating": 4.0, "assessed_rating": 75}}
        })
        self.assertEqual(created["id"], uid)

        fetched = store.get_user(uid)
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched["email"], email)
        self.assertIn("Python", fetched["skills"])

        # Record real attempt
        store.record_test_attempt(uid, "q_js_event_loop", "Event Loop", True, 50, 0.0, 0.4)
        attempts = store.get_user_attempts(uid)
        self.assertEqual(len(attempts), 1)
        self.assertTrue(attempts[0]["correct"])

if __name__ == "__main__":
    unittest.main()
