"""Runtime AI provider adapters for local Ollama and online OpenAI-compatible APIs.

Secrets stay in process memory for the current run. They are never returned to the
browser, written to SQLite, or included in logs. Progress and learner data are
stored separately in the authenticated SQLite account.
"""

import json
import os
import urllib.error
import urllib.request
from typing import Any, Dict, List, Optional


PROVIDER_PRESETS = {
    "openai": {
        "label": "OpenAI",
        "base_url": "https://api.openai.com/v1",
        "protocol": "responses",
        "models": [],
    },
    "openrouter": {
        "label": "OpenRouter",
        "base_url": "https://openrouter.ai/api/v1",
        "protocol": "chat",
        "models": [],
    },
    "groq": {
        "label": "Groq",
        "base_url": "https://api.groq.com/openai/v1",
        "protocol": "chat",
        "models": [],
    },
    "together": {
        "label": "Together AI",
        "base_url": "https://api.together.xyz/v1",
        "protocol": "chat",
        "models": [],
    },
    "deepseek": {
        "label": "DeepSeek",
        "base_url": "https://api.deepseek.com/v1",
        "protocol": "chat",
        "models": [],
    },
    "opencode": {
        "label": "OpenCode / compatible endpoint",
        "base_url": "",
        "protocol": "chat",
        "models": [],
        "requires_custom_url": True,
    },
    "custom": {
        "label": "Custom OpenAI-compatible provider",
        "base_url": "",
        "protocol": "chat",
        "models": [],
        "requires_custom_url": True,
    },
}


class AIProviderError(RuntimeError):
    pass


class AIProviderManager:
    def __init__(self):
        self._config: Optional[Dict[str, Any]] = None

    def configure(self, config: Dict[str, Any]) -> Dict[str, Any]:
        mode = config.get("mode", "offline")
        if mode not in {"offline", "online"}:
            raise AIProviderError("Model mode must be offline or online")

        context_window = int(config.get("context_window", 30720) or 30720)
        context_window = max(2048, min(32768, context_window))
        if mode == "offline":
            model = (config.get("model") or "mimo-v2.6:9b").strip()
            host = (config.get("host") or os.environ.get("OLLAMA_HOST") or "http://127.0.0.1:11434").rstrip("/")
            candidate = {"mode": "offline", "model": model, "host": host, "context_window": context_window}
            self._validate_ollama(candidate)
            self._config = candidate
        else:
            provider = config.get("provider", "openai")
            preset = PROVIDER_PRESETS.get(provider, PROVIDER_PRESETS["custom"])
            api_key = (config.get("api_key") or "").strip()
            base_url = (config.get("base_url") or preset.get("base_url") or "").strip().rstrip("/")
            model = (config.get("model") or "").strip()
            if not api_key:
                raise AIProviderError("An online provider API key is required")
            if not base_url:
                raise AIProviderError("A base URL is required for this provider")
            if not model:
                raise AIProviderError("Choose a model name for this provider")
            self._config = {
                "mode": "online",
                "provider": provider,
                "base_url": base_url,
                "protocol": preset.get("protocol", "chat"),
                "model": model,
                "api_key": api_key,
                "context_window": context_window,
            }
        return self.status()

    @staticmethod
    def _validate_ollama(config: Dict[str, Any]) -> None:
        try:
            from ollama import Client
        except ImportError as exc:
            raise AIProviderError("The ollama Python package is not installed. Run pip install -r requirements.txt") from exc
        try:
            response = Client(host=config["host"]).list()
            models = response.get("models", []) if isinstance(response, dict) else getattr(response, "models", [])
            names = []
            for model in models:
                if isinstance(model, dict):
                    names.append(model.get("name") or model.get("model"))
                else:
                    names.append(getattr(model, "model", None) or getattr(model, "name", None))
            if config["model"] not in names:
                raise AIProviderError(f"Ollama model '{config['model']}' is not installed. Run ollama pull {config['model']}.")
        except AIProviderError:
            raise
        except Exception as exc:
            raise AIProviderError(f"Could not reach Ollama at {config['host']}: {exc}") from exc

    def status(self) -> Dict[str, Any]:
        if not self._config:
            return {"configured": False, "mode": None}
        return {
            "configured": True,
            "mode": self._config["mode"],
            "provider": self._config.get("provider", "ollama"),
            "model": self._config["model"],
            "context_window": self._config["context_window"],
            "host": self._config.get("host") if self._config["mode"] == "offline" else None,
        }

    def require_configured(self) -> Dict[str, Any]:
        if not self._config:
            raise AIProviderError("Configure an AI model at startup before using an agent")
        return self._config

    @staticmethod
    def _trim_messages(messages: List[Dict[str, str]], context_window: int) -> List[Dict[str, str]]:
        # Approximate tokens conservatively without a tokenizer. Keep the system
        # instruction and the most recent turns inside a bounded context.
        budget = max(4096, context_window * 3)
        kept: List[Dict[str, str]] = []
        used = 0
        for message in reversed(messages):
            content = str(message.get("content", ""))
            cost = len(content)
            if kept and used + cost > budget:
                break
            kept.append({"role": message.get("role", "user"), "content": content})
            used += cost
        kept.reverse()
        if messages and messages[0].get("role") == "system" and (not kept or kept[0].get("role") != "system"):
            kept.insert(0, {"role": "system", "content": messages[0].get("content", "")})
        return kept

    @staticmethod
    def _extract_ollama(response: Any) -> str:
        if isinstance(response, dict):
            return str((response.get("message") or {}).get("content", ""))
        message = getattr(response, "message", None)
        return str(getattr(message, "content", "") or "")

    @staticmethod
    def _is_context_failure(error: Exception) -> bool:
        message = str(error).lower()
        return any(token in message for token in ("context", "num_ctx", "too many tokens", "out of memory", "allocat"))

    @staticmethod
    def _context_candidates(start: int) -> List[int]:
        return list(dict.fromkeys(max(2048, min(32768, value)) for value in (start, 16384, 8192, 4096, 2048)))

    def _chat_ollama(self, messages: List[Dict[str, str]], json_mode: bool = False) -> str:
        cfg = self.require_configured()
        try:
            from ollama import Client
        except ImportError as exc:
            raise AIProviderError("The ollama Python package is not installed. Run pip install -r requirements.txt") from exc
        client = Client(host=cfg["host"])
        last_error: Optional[Exception] = None
        for context_window in self._context_candidates(cfg["context_window"]):
            try:
                kwargs: Dict[str, Any] = {
                    "model": cfg["model"],
                    "messages": self._trim_messages(messages, context_window),
                    "options": {"num_ctx": context_window},
                }
                if json_mode:
                    kwargs["format"] = "json"
                text = self._extract_ollama(client.chat(**kwargs))
                cfg["context_window"] = context_window
                return text
            except Exception as exc:
                last_error = exc
                if not self._is_context_failure(exc):
                    break
        raise AIProviderError(f"Ollama request failed after context fallback: {last_error}") from last_error

    @staticmethod
    def _extract_openai_text(payload: Dict[str, Any], protocol: str) -> str:
        if protocol == "responses":
            if payload.get("output_text"):
                return str(payload["output_text"])
            for item in payload.get("output", []):
                for content in item.get("content", []):
                    if content.get("text"):
                        return str(content["text"])
            return ""
        choices = payload.get("choices") or []
        if choices:
            message = choices[0].get("message") or {}
            return str(message.get("content", ""))
        return ""

    def _chat_online(self, messages: List[Dict[str, str]], json_mode: bool = False) -> str:
        cfg = self.require_configured()
        last_error: Optional[Exception] = None
        for context_window in self._context_candidates(cfg["context_window"]):
            try:
                base_url = cfg["base_url"]
                if cfg["protocol"] == "responses":
                    url = f"{base_url}/responses"
                    body: Dict[str, Any] = {"model": cfg["model"], "input": self._trim_messages(messages, context_window)}
                    if json_mode:
                        body["text"] = {"format": {"type": "json_object"}}
                else:
                    url = f"{base_url}/chat/completions"
                    body = {"model": cfg["model"], "messages": self._trim_messages(messages, context_window), "temperature": 0.3}
                    if json_mode:
                        body["response_format"] = {"type": "json_object"}
                request = urllib.request.Request(
                    url,
                    data=json.dumps(body).encode("utf-8"),
                    headers={"Authorization": f"Bearer {cfg['api_key']}", "Content-Type": "application/json", "Accept": "application/json"},
                    method="POST",
                )
                with urllib.request.urlopen(request, timeout=90) as response:
                    payload = json.loads(response.read().decode("utf-8"))
                text = self._extract_openai_text(payload, cfg["protocol"])
                if not text:
                    raise AIProviderError("The provider returned no text")
                cfg["context_window"] = context_window
                return text
            except urllib.error.HTTPError as exc:
                detail = exc.read().decode("utf-8", errors="replace")[:500]
                last_error = AIProviderError(f"Online provider returned {exc.code}: {detail}")
            except Exception as exc:
                last_error = exc
            if last_error and not self._is_context_failure(last_error):
                break
        raise AIProviderError(f"Online provider request failed after context fallback: {last_error}") from last_error

    def chat(self, messages: List[Dict[str, str]], json_mode: bool = False) -> str:
        cfg = self.require_configured()
        if cfg["mode"] == "offline":
            return self._chat_ollama(messages, json_mode=json_mode)
        return self._chat_online(messages, json_mode=json_mode)

    def chat_json(self, messages: List[Dict[str, str]]) -> Dict[str, Any]:
        raw = self.chat(messages, json_mode=True).strip()
        try:
            return json.loads(raw)
        except json.JSONDecodeError as exc:
            start, end = raw.find("{"), raw.rfind("}")
            if start >= 0 and end > start:
                try:
                    return json.loads(raw[start:end + 1])
                except json.JSONDecodeError:
                    pass
            raise AIProviderError("The model returned invalid JSON for a structured agent task") from exc

    def list_ollama_models(self) -> List[str]:
        cfg = self._config or {"host": os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434")}
        try:
            from ollama import Client
            response = Client(host=cfg["host"]).list()
            models = response.get("models", []) if isinstance(response, dict) else getattr(response, "models", [])
            names = []
            for model in models:
                if isinstance(model, dict):
                    names.append(model.get("name") or model.get("model"))
                else:
                    names.append(getattr(model, "model", None) or getattr(model, "name", None))
            return [name for name in names if name]
        except Exception as exc:
            raise AIProviderError(f"Could not list Ollama models: {exc}") from exc


ai_provider_manager = AIProviderManager()
