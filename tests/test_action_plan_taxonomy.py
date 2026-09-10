import json
from pathlib import Path


def test_action_planning_taxonomy_primary_source_exists():
    workbook = Path(
        "plugins/eve-people-science/references/skills/manager-action-taking/Action Planning Taxonomy.xlsx"
    )
    generated = Path(
        "plugins/eve-people-science/references/skills/manager-action-taking/gen"
    )

    assert workbook.exists()
    assert workbook.stat().st_size > 1_000_000
    assert (generated / "catalog.json").exists()
    assert (generated / "question-map.json").exists()
    assert (generated / "validation-report.json").exists()
    assert (generated / "c").exists()
    assert (generated / "a").exists()
    assert not (
        Path("plugins/eve-people-science/references/skills/manager-action-taking/action_plan_taxonomy_index.json")
    ).exists()


def test_question_map_resolves_distinct_action_records():
    root = Path(
        "plugins/eve-people-science/references/skills/manager-action-taking/gen"
    )
    question_map = json.loads(
        (root / "question-map.json").read_text(encoding="utf-8")
    )
    question = question_map["questions"]["Q_ACCEPTS_FEEDBACK_360"]
    candidate_set = question["candidate_sets"][0]
    record_ids = candidate_set["action_plan_record_ids"]

    assert question_map["summary"]["question_ids"] >= 200
    assert question["display_question_id"] == "[Q_ACCEPTS_FEEDBACK_360]"
    assert candidate_set["template_name"] == "Glint 360 Accepts Feedback"
    assert len(record_ids) >= 4

    template_uuid, sequence = record_ids[0].rsplit(":", 1)
    first_record_path = (
        root / "a" / f"{template_uuid}--{int(sequence):04d}.json"
    )
    first_record = json.loads(first_record_path.read_text(encoding="utf-8"))

    assert first_record["sequence"] == 1
    assert first_record["focus_area_title"]
    assert first_record["content_description"] or first_record["content_text_body"]
    assert first_record["question_ids"] == ["Q_ACCEPTS_FEEDBACK_360"]


def test_catalog_preserves_every_workbook_row_as_an_action_record():
    root = Path(
        "plugins/eve-people-science/references/skills/manager-action-taking/gen"
    )
    catalog = json.loads((root / "catalog.json").read_text(encoding="utf-8"))
    record_files = list((root / "a").glob("*.json"))
    candidate_files = list((root / "c").glob("*.json"))

    assert catalog["summary"]["source_rows"] == 827
    assert catalog["summary"]["action_plan_records"] == 827
    assert catalog["summary"]["candidate_sets"] == 150
    assert len(record_files) == 827
    assert len(candidate_files) == 150


def test_hyphenated_question_id_is_preserved():
    question_map = json.loads(
        Path(
            "plugins/eve-people-science/references/skills/manager-action-taking/gen/question-map.json"
        ).read_text(encoding="utf-8")
    )

    assert "Q_WELL-BEING" in question_map["questions"]
    assert question_map["questions"]["Q_WELL-BEING"]["display_question_id"] == "[Q_WELL-BEING]"


def test_description_only_record_remains_actionable():
    root = Path(
        "plugins/eve-people-science/references/skills/manager-action-taking/gen/a"
    )
    records = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in root.glob("*.json")
    ]
    description_only = next(
        record
        for record in records
        if record["content_description"] and not record["content_text_body"]
    )

    assert description_only["content_type"] == "discussion_prompt"
    assert description_only["focus_area_title"]
    assert description_only["content_description"]


def test_unresolved_internal_resources_are_explicit():
    report = json.loads(
        Path(
            "plugins/eve-people-science/references/skills/manager-action-taking/gen/validation-report.json"
        ).read_text(encoding="utf-8")
    )

    assert report["status"] == "warnings"
    assert report["summary"]["unresolved_internal_references"] > 0
    assert report["unresolved_internal_references"][0]["target"]


def test_action_records_include_selection_metadata_and_resources():
    root = Path(
        "plugins/eve-people-science/references/skills/manager-action-taking/gen/a"
    )
    records = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in root.glob("*.json")
    ]

    assert all(record["action_type"] for record in records)
    assert all(record["selection_signals"] for record in records)
    assert any(record["resources"] for record in records)
    assert any(
        resource["type"] == "video"
        for record in records
        for resource in record["resources"]
    )
    assert any(
        resource["type"] in {"external_link", "inline_external"}
        for record in records
        for resource in record["resources"]
    )


def test_golden_examples_reference_authorized_records():
    base = Path("plugins/eve-people-science/references/skills/manager-action-taking")
    examples = json.loads((base / "golden-examples.json").read_text(encoding="utf-8"))["examples"]
    question_map = json.loads((base / "gen/question-map.json").read_text(encoding="utf-8"))["questions"]

    for example in examples:
        question = question_map[example["question_id"]]
        record_ids = [
            record_id
            for candidate_set in question["candidate_sets"]
            for record_id in candidate_set["action_plan_record_ids"]
        ]
        records = []
        for record_id in record_ids:
            template_uuid, sequence = record_id.rsplit(":", 1)
            records.append(
                json.loads(
                    (
                        base
                        / "gen/a"
                        / f"{template_uuid}--{int(sequence):04d}.json"
                    ).read_text(encoding="utf-8")
                )
            )

        titles = {record["focus_area_title"] for record in records}
        action_types = {record["action_type"] for record in records}
        assert set(example["recommended_candidate_titles"]) & titles
        assert set(example["preferred_action_types"]) & action_types
        assert example["act_application"]
        assert example["manager_role"] in {"coach", "facilitator", "roadblock_remover", "connector"}
        assert example["secondary_context_to_use"]
        assert example["why_action_matters"]
        assert example["presentation_packaging"]


def test_act_secondary_context_is_loaded_by_mat_skill():
    base = Path("plugins/eve-people-science/references/skills/manager-action-taking")
    skill = Path(
        "plugins/eve-people-science/skills/manager-action-taking/SKILL.md"
    ).read_text(encoding="utf-8")
    secondary = (base / "secondary/collaborative-action-taking-act.md").read_text(encoding="utf-8")

    assert "collaborative-action-taking-act.md" in skill
    assert "ACT conversation guide" in skill
    assert "Acknowledge where we are" in secondary
    assert "Collaborate on where we want to go" in secondary
    assert "Take one step forward together" in secondary
    assert "7x more likely to report being disengaged" in secondary
    assert "7% increased scores on average" in secondary


def test_psychological_safety_secondary_context_is_loaded_by_mat_skill():
    base = Path("plugins/eve-people-science/references/skills/manager-action-taking")
    skill = Path(
        "plugins/eve-people-science/skills/manager-action-taking/SKILL.md"
    ).read_text(encoding="utf-8")
    secondary = (base / "secondary/psychological-safety-techcommunity.md").read_text(encoding="utf-8")

    assert "psychological-safety-techcommunity.md" in skill
    assert "Check negative reactivity" in secondary
    assert "Listen without agenda" in secondary
    assert "Model the vulnerability you hope to see" in secondary
    assert "4x as likely" in secondary
    assert "31%" in secondary


def test_presentation_template_is_tertiary_context_only():
    base = Path("plugins/eve-people-science/references/skills/manager-action-taking")
    skill = Path(
        "plugins/eve-people-science/skills/manager-action-taking/SKILL.md"
    ).read_text(encoding="utf-8")
    tertiary = (base / "tertiary/action-taking-presentation-template.md").read_text(encoding="utf-8")

    assert "action-taking-presentation-template.md" in skill
    assert "only when the user asks for a presentation" in skill
    assert "This is a tertiary source. It should not affect action-record selection." in tertiary
    assert "Adoption & Actions Storytelling Deck Updated for PS 2.0.pptx" in tertiary


def test_selection_logic_uses_secondary_and_tertiary_lenses():
    logic = Path(
        "plugins/eve-people-science/references/skills/manager-action-taking/selection-logic.md"
    ).read_text(encoding="utf-8")

    assert "Decision phases" in logic
    assert "Manager-role lens" in logic
    assert "Anti-selection rules" in logic
    assert "Presentation packaging behavior" in logic
    assert "The user asks for a deck or presentation" in logic
    assert "The issue is systemic or outside the manager's control" in logic


def test_manager_action_skill_declares_taxonomy_as_primary_source():
    skill = Path(
        "plugins/eve-people-science/skills/manager-action-taking/SKILL.md"
    ).read_text(encoding="utf-8")

    assert "Action Planning Taxonomy workbook" in skill
    assert "gen/question-map.json" in skill
    assert "Each workbook row is a distinct focus-area action option" in skill
    assert "selection-logic.md" in skill
    assert "Action type:" in skill
    assert "Do not combine all matched records into one mandatory multi-step plan." in skill
    assert "Do not generate generic action advice when a taxonomy match exists." in skill
