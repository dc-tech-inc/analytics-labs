# Contributing

1. Branch from `main` (`feat/...`, `fix/...`) and use [Conventional Commits](https://www.conventionalcommits.org/).
2. Run the checks for the folder you touched (see the README, section "Run it"):
   `ruff check . && ruff format --check . && pytest` in `python/` or `marketing-ga4-synthetic/`,
   `Rscript tests/testthat.R && quarto render report.qmd` in `r-quarto/`.
3. If you change a statistic in `python/`, regenerate the reference numbers with
   `python -m penguin_lab.cli stats` and commit `data/expected_stats.json`; the R tests read it.
4. Open a pull request. CI must be green; maintainers merge with a merge commit (no squash).
5. Never commit secrets, real analytics exports or personal data. Synthetic data only, on `example.test` hosts.
6. Behaviour changes need a test; decisions worth remembering get a short ADR in `docs/adr/`.
