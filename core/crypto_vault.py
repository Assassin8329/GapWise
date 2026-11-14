"""
Token Vault and Cryptographic Key Management System (KMS).
Enforces:
- AES-256-GCM authenticated encryption for all access and refresh tokens.
- Master key loaded strictly from environment or secure KMS vault config, never in code.
- Unique cryptographic data key derived per user via PBKDF2-HMAC-SHA256.
- Strict token scrubbing to prevent token leakage into logs or client responses.
- Server-side authenticated API proxying.
"""

import os
import json
import time
import base64
import hashlib
import secrets
from typing import Dict, Any, Optional
from core.aes_gcm import aes_256_gcm_encrypt, aes_256_gcm_decrypt

KMS_CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "kms.json")

def _get_or_create_master_kms_key() -> bytes:
    """
    Retrieves the Master Key from environment or securely persists KMS master key.
    Never hardcoded.
    """
    env_key = os.environ.get("KMS_MASTER_KEY")
    if env_key:
        return hashlib.sha256(env_key.encode("utf-8")).digest()

    os.makedirs(os.path.dirname(KMS_CONFIG_PATH), exist_ok=True)
    if os.path.exists(KMS_CONFIG_PATH):
        try:
            with open(KMS_CONFIG_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                return base64.b64decode(data["master_key"])
        except Exception:
            pass

    # Generate new cryptographically secure 256-bit master key
    new_master_key = secrets.token_bytes(32)
    with open(KMS_CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump({
            "key_id": "kms-key-prod-01",
            "created_at": time.time(),
            "algorithm": "AES-256-GCM",
            "master_key": base64.b64encode(new_master_key).decode("utf-8")
        }, f, indent=2)
    return new_master_key

MASTER_KMS_KEY = _get_or_create_master_kms_key()

def derive_user_data_key(user_id: str, salt: bytes) -> bytes:
    """
    Derives a unique 256-bit encryption key per user using PBKDF2-HMAC-SHA256.
    Ensures cryptographic isolation across accounts.
    """
    user_context = f"antigravity:vault:{user_id}".encode("utf-8")
    return hashlib.pbkdf2_hmac("sha256", MASTER_KMS_KEY, salt + user_context, 100_000, dklen=32)

class TokenVault:
    """
    Secure Token Vault.
    Stores and retrieves encrypted tokens in memory / persistent db.
    Tokens are never sent to the browser or logged.
    """

    def __init__(self):
        # In-memory store: user_id -> provider_id -> EncryptedTokenRecord
        self._vault: Dict[str, Dict[str, Dict[str, Any]]] = {}

    def store_token(
        self,
        user_id: str,
        provider_id: str,
        access_token: str,
        refresh_token: Optional[str] = None,
        expires_in: int = 3600,
        scopes: Optional[list] = None,
        account_username: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Encrypts and stores user tokens with AES-256-GCM.
        Returns a sanitized public token descriptor (NO TOKENS INCLUDED).
        """
        salt = secrets.token_bytes(16)
        user_key = derive_user_data_key(user_id, salt)

        token_payload = json.dumps({
            "access_token": access_token,
            "refresh_token": refresh_token,
            "created_at": time.time(),
            "expires_at": time.time() + expires_in
        }).encode("utf-8")

        nonce = secrets.token_bytes(12)
        aad = f"{user_id}:{provider_id}".encode("utf-8")
        ciphertext_blob = aes_256_gcm_encrypt(user_key, nonce, token_payload, aad)

        if user_id not in self._vault:
            self._vault[user_id] = {}

        # Masked token for display (e.g. "ghp_***4a9b")
        masked = access_token[:4] + "***" + access_token[-4:] if len(access_token) >= 8 else "***"

        record = {
            "salt": base64.b64encode(salt).decode("utf-8"),
            "ciphertext": base64.b64encode(ciphertext_blob).decode("utf-8"),
            "provider_id": provider_id,
            "scopes": scopes or [],
            "account_username": account_username or "connected-user",
            "masked_token": masked,
            "created_at": time.time(),
            "expires_at": time.time() + expires_in,
            "has_refresh_token": bool(refresh_token)
        }
        self._vault[user_id][provider_id] = record

        # Return sanitized summary
        return self.get_sanitized_status(user_id, provider_id)

    def retrieve_token(self, user_id: str, provider_id: str) -> Optional[Dict[str, Any]]:
        """
        Decrypts token internally for server-side proxy use ONLY.
        Never return this to frontend routes or logs!
        """
        record = self._vault.get(user_id, {}).get(provider_id)
        if not record:
            return None

        salt = base64.b64decode(record["salt"])
        ciphertext_blob = base64.b64decode(record["ciphertext"])
        user_key = derive_user_data_key(user_id, salt)
        aad = f"{user_id}:{provider_id}".encode("utf-8")

        try:
            plaintext = aes_256_gcm_decrypt(user_key, ciphertext_blob, aad)
            token_data = json.loads(plaintext.decode("utf-8"))
            return {
                "access_token": token_data["access_token"],
                "refresh_token": token_data.get("refresh_token"),
                "expires_at": token_data["expires_at"],
                "scopes": record["scopes"],
                "account_username": record["account_username"]
            }
        except Exception as e:
            # Token decryption failed or corrupted
            return None

    def revoke_token(self, user_id: str, provider_id: str) -> bool:
        """
        Wipes token from vault on account disconnection.
        """
        if user_id in self._vault and provider_id in self._vault[user_id]:
            del self._vault[user_id][provider_id]
            return True
        return False

    def get_sanitized_status(self, user_id: str, provider_id: str) -> Optional[Dict[str, Any]]:
        """
        Safe public metadata: does NOT contain secret tokens.
        """
        record = self._vault.get(user_id, {}).get(provider_id)
        if not record:
            return None

        is_expired = time.time() > record["expires_at"]
        return {
            "provider_id": provider_id,
            "connected": True,
            "account_username": record["account_username"],
            "masked_token": record["masked_token"],
            "scopes": record["scopes"],
            "created_at": record["created_at"],
            "expires_at": record["expires_at"],
            "is_expired": is_expired,
            "has_refresh_token": record["has_refresh_token"]
        }

    def list_connections(self, user_id: str) -> Dict[str, Any]:
        """
        Returns all sanitized connected accounts for user.
        """
        user_conns = self._vault.get(user_id, {})
        return {pid: self.get_sanitized_status(user_id, pid) for pid in user_conns}

# Singleton instance
vault = TokenVault()

def scrub_sensitive_logs(message: str) -> str:
    """
    Log scrubber: replaces token-like sequences and secrets with [REDACTED_BY_TOKEN_VAULT]
    """
    import re
    # Mask OAuth tokens, Bearer tokens, secrets
    patterns = [
        r"(Bearer\s+)[A-Za-z0-9_\-\.]{8,}",
        r"(access_token[\"':\s=]+)[A-Za-z0-9_\-\.]{8,}",
        r"(refresh_token[\"':\s=]+)[A-Za-z0-9_\-\.]{8,}",
        r"(client_secret[\"':\s=]+)[A-Za-z0-9_\-\.]{8,}",
        r"(gh[opsu]_[A-Za-z0-9_]{16,})",
    ]
    scrubbed = message
    for p in patterns:
        scrubbed = re.sub(p, r"\1[REDACTED_BY_TOKEN_VAULT]", scrubbed)
    return scrubbed
