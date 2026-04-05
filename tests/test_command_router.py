import pytest
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from command_router import CommandRouter, COMMAND_MAP_PATH

@pytest.fixture(scope="module")
def router():
    return CommandRouter(COMMAND_MAP_PATH)

def test_command_map_loads(router):
    assert isinstance(router.command_map, dict)
    assert len(router.command_map) >= 20

def test_known_command_resolves(router):
    cmd = "/wa_followup_quote"
    mapping = router.resolve_command(cmd)
    assert mapping is not None
    assert mapping["channel"] == "whatsapp"
    assert "query_hint" in mapping

def test_unknown_command_returns_none(router):
    mapping = router.resolve_command("/not_a_command")
    assert mapping is None

def test_run_command_known(router):
    result = router.run_command("/wa_followup_quote")
    assert result["status"] == "ok"
    assert result["mapping"]["use_case"] == "follow_up_after_quote"
    assert "query_hint" in result["mapping"]

def test_run_command_unknown(router):
    result = router.run_command("/not_a_command")
    assert result["status"] == "not_found"
    assert result["result"] is None

def test_no_crash_on_incomplete_map(tmp_path):
    # Create a minimal/incomplete map
    incomplete_map = {"/test": {"intent": "client_reply"}}
    test_map_path = tmp_path / "command_map.json"
    with open(test_map_path, "w", encoding="utf-8") as f:
        import json; json.dump(incomplete_map, f)
    router = CommandRouter(str(test_map_path))
    result = router.run_command("/test")
    assert result["status"] == "ok"
    assert "mapping" in result
