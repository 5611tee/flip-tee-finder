
# Flip Tee Finder

A tiny Streamlit app that scores vintage T‑shirts for *quick‑flip* potential and generates a listing checklist & SEO title.

## How to run
1. Install dependencies:
```bash
pip install streamlit pandas
```
2. Launch the app (from this folder):
```bash
streamlit run app.py
```

## Files
- `app.py` — the app
- `data/valuable_tags.csv` — tags & weights
- `data/high_value_keywords.csv` — value keywords & weights

## Notes
- Scores are heuristic. Always check comps on marketplaces.
- Update the CSVs to tune to your niche or region.
