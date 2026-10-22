# r-quarto

Statistical analysis of the Palmer penguins in R: descriptive statistics, Welch t-test, a linear model and a ggplot2
figure, written up as a Quarto report (`report.qmd`).

```bash
Rscript tests/testthat.R     # testthat; also compares with ../data/expected_stats.json (computed in Python)
quarto render report.qmd     # writes report.html (self-contained)
```

Requires R >= 4.1, Quarto, and the packages listed in `DESCRIPTION` (`dplyr`, `ggplot2`, `jsonlite`, `knitr`, `readr`,
`rmarkdown`, `testthat`, `tibble`). Dataset licence and citation: [`../data/README.md`](../data/README.md).
Docs: <https://quarto.org/docs/computations/r.html>, <https://testthat.r-lib.org/>.
