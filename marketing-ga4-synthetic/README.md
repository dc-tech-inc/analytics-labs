# marketing-ga4-synthetic

**Synthetic data only.** A seeded generator plus a reporting pipeline for GA4 BigQuery-export-shaped events, a Search
Console CSV and an Ads CSV. Standard library only.

```bash
pip install -e ".[dev]"
ga4-synth generate --seed 7 --days 28   # writes data/ (git-ignored, about 25 MB)
ga4-synth report                        # writes dist/report.json and dist/index.html
pytest
```

Pipeline steps (`src/ga4_synth/pipeline.py`): group events into sessions by `user_pseudo_id` + `ga_session_id`,
assign a simplified channel group, count engaged sessions (10 s, a key event, or 2+ page views), compute conversion and
revenue per channel, ad CPC/CPA/ROAS per campaign (ROAS uses GA revenue of the matching channel), and Search Console
CTR with impression-weighted average position. Schema reference: <https://support.google.com/analytics/answer/7029846>.
