import json
from pathlib import Path
from lab.providers.dataforseo import DataForSEOProvider

STARTER={
"dataforseo_labs/google/keyword_suggestions/live",
"dataforseo_labs/google/related_keywords/live",
"keywords_data/google_ads/search_volume/live",
"dataforseo_labs/google/bulk_keyword_difficulty/live",
"serp/google/organic/live/advanced",
"ai_optimization/chat_gpt/llm_scraper/live/advanced",
}

def test_starter_six_are_catalogued():
    catalog=DataForSEOProvider().catalog
    assert STARTER <= set(catalog)

def test_unknown_or_unapproved_cost_returns_none(tmp_path):
    path=tmp_path/"catalog.json"; path.write_text(json.dumps({"dataforseo":{"x":{"cost_usd":None}}}))
    assert DataForSEOProvider(path).estimate_cost("x",{}) is None

def test_skill_is_one_job_and_under_500_lines():
    text=(Path(__file__).parents[1]/"skills/keyword-research/SKILL.md").read_text()
    assert len(text.splitlines()) < 500
    assert "Does not write content or strategy" in text
