import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_manifest_schema_is_versioned():
    schema_path = ROOT / "schemas/analysis-manifest.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    assert schema["properties"]["schema_version"]["const"] == "1.0.0"


def test_plugin_manifest_matches_standalone_layout():
    manifest = json.loads(
        (ROOT / ".claude-plugin/plugin.json").read_text(encoding="utf-8")
    )

    assert manifest["name"] == "eve-people-science"
    assert manifest["version"] == "2.1.0"
    assert "mcpServers" not in manifest
