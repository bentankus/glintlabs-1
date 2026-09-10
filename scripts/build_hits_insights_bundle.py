#!/usr/bin/env python3
"""Build the portable HITs Study Insights skill and MCP bundle."""

from __future__ import annotations

import argparse
import json
import shutil
import tempfile
import zipfile
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = PLUGIN_ROOT.parents[1]
SKILL_NAME = "hits-study-insights"
BUNDLE_NAME = "hits-study-insights-mcp"
MCP_ENDPOINT = "https://mcp.hits.microsoft.com"
DEFAULT_GROUP = "https://hits.microsoft.com/group/people-science"
DEFAULT_OUTPUT = REPO_ROOT / "dist" / f"{BUNDLE_NAME}.zip"
FIXED_TIMESTAMP = (2026, 8, 24, 0, 0, 0)
def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")


def write_deterministic_zip(source: Path, output: Path) -> None:
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(source.rglob("*")):
            if not path.is_file():
                continue
            info = zipfile.ZipInfo(
                str(path.relative_to(source.parent)).replace("\\", "/"),
                FIXED_TIMESTAMP,
            )
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            archive.writestr(info, path.read_bytes())


def build_bundle(output: Path) -> Path:
    output = output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)

    plugin = json.loads(
        (PLUGIN_ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8")
    )

    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir) / BUNDLE_NAME
        skill_dir = root / "skills" / SKILL_NAME
        refs_dir = skill_dir / "references"
        refs_dir.mkdir(parents=True)

        shutil.copy2(
            PLUGIN_ROOT / "skills" / SKILL_NAME / "SKILL.md",
            skill_dir / "SKILL.md",
        )
        for reference in sorted(
            (PLUGIN_ROOT / "references" / "skills" / SKILL_NAME).glob("*.md")
        ):
            shutil.copy2(reference, refs_dir / reference.name)

        write_json(
            root / "mcp.json",
            {"mcpServers": {"hits": plugin["mcpServers"]["hits"]}},
        )
        write_json(
            root / "bundle.json",
            {
                "name": BUNDLE_NAME,
                "version": plugin["version"],
                "skill": SKILL_NAME,
                "mcpServer": "hits",
                "mcpEndpoint": MCP_ENDPOINT,
                "defaultGroup": DEFAULT_GROUP,
                "containsCredentials": False,
                "installPrompt": (
                    "Extract and load this folder as a skill and MCP. Install the "
                    "skill for my user, merge mcp.json into my MCP configuration "
                    "without removing existing servers, authenticate if required, "
                    "and verify that HITs queries default to the People Science group."
                ),
            },
        )
        (root / "README.md").write_text(
            f"""# HITs Study Insights skill and MCP

This portable bundle contains the `{SKILL_NAME}` skill and the HITs MCP connection.

## Give this instruction to an agent

> Extract and load this folder as a skill and MCP. Install the skill for my user,
> merge `mcp.json` into my MCP configuration without removing existing servers,
> authenticate if required, and verify that HITs queries default to the People
> Science group.

## Agent installation contract

1. Extract the ZIP without changing its internal structure.
2. Install `skills/{SKILL_NAME}/` as a user-level skill, including `references/`.
3. Merge the `hits` entry from `mcp.json` into the active user MCP configuration.
   Preserve every existing MCP server.
4. Permit `{MCP_ENDPOINT}` if the host uses a URL allowlist.
5. Reload or restart the host so the new skill and MCP tools are discovered.
6. Complete Microsoft authentication when prompted.
7. Verify that HITs tools are available and that the skill defaults retrieval to
   `{DEFAULT_GROUP}`.

An enterprise policy can still block an unapproved MCP server. Local configuration
must not attempt to bypass that policy.

## Contents

- `skills/{SKILL_NAME}/SKILL.md`
- `skills/{SKILL_NAME}/references/`
- `mcp.json`
- `bundle.json`

The bundle contains no credentials, tokens, or user-specific filesystem paths.
""",
            encoding="utf-8",
        )

        write_deterministic_zip(root, output)

    return output


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build the portable HITs Study Insights bundle."
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    print(build_bundle(args.output))


if __name__ == "__main__":
    main()
