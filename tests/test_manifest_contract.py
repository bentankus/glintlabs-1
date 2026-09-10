import json
from pathlib import Path


def test_manifest_schema_is_versioned():
    schema_path = Path("plugins/eve-people-science/schemas/analysis-manifest.schema.json")
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    assert schema["properties"]["schema_version"]["const"] == "1.0.0"


def test_dual_manifest_entries_match():
    left = json.loads(Path(".claude-plugin/marketplace.json").read_text(encoding="utf-8"))
    right = json.loads(Path(".github/plugin/marketplace.json").read_text(encoding="utf-8"))
    left_entry = next(
        plugin for plugin in left["plugins"] if plugin["name"] == "eve-people-science"
    )
    right_entry = next(
        plugin for plugin in right["plugins"] if plugin["name"] == "eve-people-science"
    )
    assert left_entry == right_entry
