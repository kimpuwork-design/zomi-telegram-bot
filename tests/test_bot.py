"""Isolated tests: no Telegram or Supabase credentials/network calls required."""

import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace

import pytest


@pytest.fixture
def bot_app(monkeypatch):
    state = {"inserted": [], "reply_texts": [], "updates": [], "fail_insert": False}

    class FakeQuery:
        def insert(self, record):
            self.record = record
            return self

        def execute(self):
            if state["fail_insert"]:
                raise RuntimeError("sensitive database diagnostics")
            state["inserted"].append(self.record)
            return SimpleNamespace(data=[self.record], count=1)

    class FakeBot:
        def __init__(self, token, threaded):
            assert token == "test-telegram-token"
            assert threaded is False
            self.handlers = {}
            state["bot"] = self

        def message_handler(self, commands=None, func=None):
            def decorator(handler):
                self.handlers["start" if commands else "message"] = handler
                return handler
            return decorator

        def process_new_updates(self, updates):
            state["updates"].extend(updates)

        def reply_to(self, message, text):
            state["reply_texts"].append(text)

    telebot = ModuleType("telebot")
    telebot.TeleBot = FakeBot
    telebot.types = SimpleNamespace(
        Update=SimpleNamespace(de_json=lambda raw: json.loads(raw))
    )

    supabase = ModuleType("supabase")
    supabase.Client = object

    def fake_create_client(url, key):
        assert url == "https://example.supabase.co"
        assert key == "test-supabase-key"
        return SimpleNamespace(table=lambda name: FakeQuery() if name == "zomi_dictionary" else None)

    supabase.create_client = fake_create_client
    monkeypatch.setitem(sys.modules, "telebot", telebot)
    monkeypatch.setitem(sys.modules, "supabase", supabase)
    monkeypatch.setenv("TELEGRAM_TOKEN", "test-telegram-token")
    monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("SUPABASE_KEY", "test-supabase-key")
    monkeypatch.delenv("TELEGRAM_WEBHOOK_SECRET", raising=False)

    path = Path(__file__).resolve().parents[1] / "api" / "index.py"
    spec = importlib.util.spec_from_file_location("zomi_bot_test_target", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.app.config["TESTING"] = True
    return module, state


def make_message(text):
    return SimpleNamespace(text=text, from_user=SimpleNamespace(id=12345))


def test_health_endpoint(bot_app):
    module, _ = bot_app
    response = module.app.test_client().get("/")
    assert response.status_code == 200
    assert b"Zomi AI Bot" in response.data


def test_webhook_accepts_valid_update_without_optional_secret(bot_app):
    module, state = bot_app
    response = module.app.test_client().post(
        "/telegram",
        json={"update_id": 123},
    )
    assert response.status_code == 200
    assert state["updates"] == [{"update_id": 123}]


def test_webhook_rejects_invalid_json(bot_app):
    module, state = bot_app
    response = module.app.test_client().post(
        "/", data="not-json", content_type="application/json"
    )
    assert response.status_code == 400
    assert not state["updates"]


def test_webhook_rejects_oversized_update(bot_app):
    module, state = bot_app
    response = module.app.test_client().post(
        "/", data="x" * (64 * 1024 + 1), content_type="application/json"
    )
    assert response.status_code == 413
    assert not state["updates"]


def test_secret_authentication_when_configured(bot_app, monkeypatch):
    module, state = bot_app
    monkeypatch.setenv("TELEGRAM_WEBHOOK_SECRET", "expected-secret")
    unauthorized = module.app.test_client().post("/", json={"update_id": 1})
    assert unauthorized.status_code == 403
    authorized = module.app.test_client().post(
        "/",
        json={"update_id": 2},
        headers={"X-Telegram-Bot-Api-Secret-Token": "expected-secret"},
    )
    assert authorized.status_code == 200
    assert state["updates"] == [{"update_id": 2}]


def test_start_message_has_instructions(bot_app):
    _, state = bot_app
    state["bot"].handlers["start"](make_message("/start"))
    assert "Zomi" in state["reply_texts"][0]


def test_two_required_languages_are_stored(bot_app):
    _, state = bot_app
    state["bot"].handlers["message"](make_message("Zomi phrase, မြန်မာဘာသာ"))
    assert state["inserted"] == [{
        "zomi_text": "Zomi phrase",
        "burmese_text": "မြန်မာဘာသာ",
        "english_text": "",
        "category": "General",
        "added_by": "12345",
    }]


def test_four_language_fields_are_stored(bot_app):
    _, state = bot_app
    state["bot"].handlers["message"](
        make_message("Na dam hia?, နေကောင်းလား?, How are you?, Greeting")
    )
    assert state["inserted"][0]["english_text"] == "How are you?"
    assert state["inserted"][0]["category"] == "Greeting"


@pytest.mark.parametrize("text", [
    None,
    "missing delimiter",
    ", Burmese text",
    "Zomi text, ",
    "x" * 2001,
    "a, b, c, d, unexpected fifth field",
])
def test_invalid_submissions_do_not_write(bot_app, text):
    _, state = bot_app
    state["bot"].handlers["message"](make_message(text))
    assert state["inserted"] == []
    assert state["reply_texts"]


def test_database_exception_is_not_leaked_to_contributor(bot_app):
    _, state = bot_app
    state["fail_insert"] = True
    state["bot"].handlers["message"](make_message("Zomi, Burmese"))
    assert not state["inserted"]
    assert state["reply_texts"]
    assert all("sensitive database diagnostics" not in reply for reply in state["reply_texts"])
