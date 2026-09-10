import importlib.util
import json
import zipfile
from pathlib import Path


SCRIPT = Path(
    "plugins/eve-people-science/scripts/build_hits_insights_bundle.py"
)
PLUGIN_ROOT = Path("plugins/eve-people-science")


def load_builder():
    spec = importlib.util.spec_from_file_location("build_hits_insights_bundle", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_bundle_contains_portable_skill_and_mcp(tmp_path):
    builder = load_builder()
    output = builder.build_bundle(tmp_path / "bundle.zip")
    root = "hits-study-insights-mcp"

    with zipfile.ZipFile(output) as archive:
        names = set(archive.namelist())
        required = {
            f"{root}/README.md",
            f"{root}/bundle.json",
            f"{root}/mcp.json",
            f"{root}/skills/hits-study-insights/SKILL.md",
            f"{root}/skills/hits-study-insights/references/README.md",
            f"{root}/skills/hits-study-insights/references/topic-lexicon.md",
            f"{root}/skills/hits-study-insights/references/study-topic-profile.md",
            f"{root}/skills/hits-study-insights/references/retrieval-playbook.md",
            f"{root}/skills/hits-study-insights/references/golden-example.md",
        }
        assert required <= names

        mcp = json.loads(archive.read(f"{root}/mcp.json"))
        metadata = json.loads(archive.read(f"{root}/bundle.json"))
        all_text = b"\n".join(archive.read(name) for name in sorted(names))

    assert mcp["mcpServers"]["hits"]["args"][-1] == (
        "https://mcp.hits.microsoft.com"
    )
    assert metadata["defaultGroup"] == (
        "https://hits.microsoft.com/group/people-science"
    )
    assert metadata["containsCredentials"] is False
    assert b"C:\\Users\\" not in all_text
    assert b"client_secret" not in all_text.lower()


def test_hits_mcp_is_declared_in_plugin_manifest():
    plugin = json.loads(
        (PLUGIN_ROOT / ".claude-plugin/plugin.json").read_text(encoding="utf-8")
    )
    hits = plugin["mcpServers"]["hits"]

    assert hits["command"] == "agency"
    assert hits["args"] == [
        "mcp",
        "remote",
        "--url",
        "https://mcp.hits.microsoft.com",
    ]
