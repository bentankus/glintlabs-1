from pathlib import Path


def test_each_skill_has_first_priority_reference_folder():
    skills_dir = Path("plugins/eve-people-science/skills")
    refs_dir = Path("plugins/eve-people-science/references/skills")
    skill_names = sorted(path.name for path in skills_dir.iterdir() if path.is_dir())

    missing = [
        name
        for name in skill_names
        if not (refs_dir / name / "README.md").exists()
    ]

    assert missing == []


def test_analyze_survey_points_to_demo_data():
    skill = Path("plugins/eve-people-science/skills/analyze-survey/SKILL.md").read_text(encoding="utf-8")
    demo_config = Path("plugins/eve-people-science/demo-data/survey/config.json")
    demo_csv = Path("plugins/eve-people-science/demo-data/survey/glint_demo_data.csv")

    assert "Do you have survey data you would like to reference? If not, you can use demo data." in skill
    assert demo_config.exists()
    assert demo_csv.exists()


def test_hits_study_insights_contract():
    skill = Path(
        "plugins/eve-people-science/skills/hits-study-insights/SKILL.md"
    ).read_text(encoding="utf-8")

    body_rank = skill.index("**Prompt-topic frequency within each study**")
    coverage_rank = skill.index("**Prompt-topic coverage within each study**")
    tag_rank = skill.index("**Tag/topic relevance**")
    date_rank = skill.index("**Publication date**")

    assert body_rank < coverage_rank < tag_rank < date_rank
    assert "Do not use study titles" in skill
    assert "term frequency" in skill
    assert "document frequency" in skill
    assert "keyword coverage" in skill
    assert "topic-lexicon.md" in skill
    assert "study-topic-profile.md" in skill
    assert "retrieval-playbook.md" in skill
    assert "golden-example.md" in skill
    assert "historical lexicon counts" in skill
    assert "must not be used to exclude a curated group member" in skill
    assert "do not report corpus-wide frequencies" in skill
    assert "topic_frequency = sum(normalized body occurrences * topic weight)" in skill
    assert "summed prompt-topic frequency" in skill
    assert "supporting\nstudy links on a separate `Sources:` line immediately below" in skill
    assert "Do not defer\nall citations to a source list at the end." in skill
    assert "## Cross-study summary" in skill
    assert "supports, contradicts, or does not address" in skill
    assert "Do not place a single-study claim in the cross-study summary." in skill
    assert "Never score generic actor or\naction words" in skill
    assert "Never treat a tool call's `COMPLETED` status" in skill
    assert "Select the top five studies." in skill
    assert "at least two selected studies" in skill
    assert "quantitative and qualitative evidence" in skill
    assert "https://hits.microsoft.com/group/people-science" in skill

    lexicon = Path(
        "plugins/eve-people-science/references/skills/"
        "hits-study-insights/topic-lexicon.md"
    ).read_text(encoding="utf-8")
    for topic in (
        "AI transformation",
        "AI tools",
        "AI adoption",
        "AI agents",
        "AI value",
        "Psychological safety",
        "Viva Glint",
        "Employee feedback",
        "Action taking",
        "Employee surveys",
    ):
        assert topic in lexicon

    profile = Path(
        "plugins/eve-people-science/references/skills/"
        "hits-study-insights/study-topic-profile.md"
    ).read_text(encoding="utf-8")
    assert profile.count("https://hits.microsoft.com/study/") == 29
    assert "A study may discuss multiple topics." in profile

    playbook = Path(
        "plugins/eve-people-science/references/skills/"
        "hits-study-insights/retrieval-playbook.md"
    ).read_text(encoding="utf-8")
    assert "response may stop at 20 records" in playbook
    assert "record-level `group` field" in playbook
    assert "Sustainable Copilot adoption" in playbook
    assert "Make sure my team uses AI" in playbook

    golden_example = Path(
        "plugins/eve-people-science/references/skills/"
        "hits-study-insights/golden-example.md"
    ).read_text(encoding="utf-8")
    assert "## Cross-study summary" in golden_example
    assert "**Source:**" in golden_example
