# Dataset: Palmer Archipelago penguins

`penguins.csv` is the simplified table from the `palmerpenguins` package (344 rows, 8 columns).

- **Original source:** Gorman KB, Williams TD, Fraser WR (2014). Ecological sexual dimorphism and environmental
  variability within a community of Antarctic penguins (genus *Pygoscelis*). PLoS ONE 9(3):e90081.
  <https://doi.org/10.1371/journal.pone.0090081> (data collected by Dr. Kristen Gorman at Palmer Station, Antarctica LTER).
- **Packaging:** Horst AM, Hill AP, Gorman KB (2020). *palmerpenguins: Palmer Archipelago (Antarctica) penguin data.*
  R package version 0.1.0. <https://doi.org/10.5281/zenodo.3960218>, <https://github.com/allisonhorst/palmerpenguins>
- **License:** CC0 1.0 (public domain dedication), released in accordance with the Palmer Station LTER Data Policy.
  Redistribution is allowed; please keep this citation.
- **Missing values:** written as `NA`; the analyses use complete cases only (333 rows).

`expected_stats.json` is produced by the Python code (`python -m penguin_lab.cli stats`) and is read by the R tests,
so the two implementations are checked against each other.
