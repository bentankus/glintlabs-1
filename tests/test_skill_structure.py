from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_each_skill_has_first_priority_reference_folder():
    skills_dir = ROOT / "skills"
    refs_dir = ROOT / "references/skills"
    skill_names = sorted(path.name for path in skills_dir.iterdir() if path.is_dir())

    assert skill_names == [
        "analysis-qa",
        "analyze-survey",
        "interpret-analysis",
        "people-science-knowledge-vault",
    ]

    missing = [
        name
        for name in skill_names
        if not (refs_dir / name / "README.md").exists()
    ]

    assert missing == []


def test_analyze_survey_points_to_demo_data():
    skill = (ROOT / "skills/analyze-survey/SKILL.md").read_text(encoding="utf-8")
    demo_config = ROOT / "demo-data/survey/config.json"
    demo_csv = ROOT / "demo-data/survey/glint_demo_data.csv"

    assert "Do you have survey data you would like to reference? If not, you can use demo data." in skill
    assert demo_config.exists()
    assert demo_csv.exists()


def test_knowledge_vault_source_priority():
    skill = (ROOT / "skills/people-science-knowledge-vault/SKILL.md").read_text(
        encoding="utf-8"
    )
    sources = (
        ROOT / "references/skills/people-science-knowledge-vault/source-priority.md"
    ).read_text(encoding="utf-8")

    assert "Microsoft Viva Blog" in skill
    assert "only article records from the `External` worksheet" in skill
    assert "microsoftvivablog" in sources
    assert "People_Science_Content_full_index.xlsx" in sources
    assert "`External`" in sources
    assert "`Internal PSEs & POVs`" in sources
