# 0002: Python is the reference for R

**Status:** accepted

**Context.** The same analysis exists in two languages. If they drift, the repo stops proving anything about either.
R and Quarto are not installed on the author's machine, so R cannot be run locally; CI is the only place it executes.

**Decision.** Python computes the reference numbers and writes `data/expected_stats.json`. The R `testthat` suite reads
that file and asserts equality within 1e-8. A Python test asserts the file matches what the code computes now.

**Consequences.** A disagreement between the languages fails CI in either direction, and R correctness gets an
independent check despite never running locally. Cost: changing a statistic means regenerating one JSON file
(documented in CONTRIBUTING). Alternative rejected: hard-coding expected values in the R tests, which would silently
diverge from the Python side.
