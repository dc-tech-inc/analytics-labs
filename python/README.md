# python

The same analysis as `../r-quarto` in pandas and SciPy, plus a deliberately simple scikit-learn classifier
(standardised logistic regression predicting species, stratified 75/25 split, seed 42, 5-fold CV).

```bash
pip install -e ".[dev]"
pytest
python -m penguin_lab.cli stats      # prints the summary table and rewrites ../data/expected_stats.json
python -m penguin_lab.cli model      # accuracy and confusion matrix as JSON
python -m penguin_lab.cli figures    # outputs/flipper_vs_mass.png
```
