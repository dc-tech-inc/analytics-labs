# 0001: Palmer penguins as the public dataset

**Status:** accepted

**Context.** The analysis needs a public dataset with a clear licence, small enough to commit, usable offline by both R
and Python, and with a real statistical story (group differences, a continuous relationship, a classification task).

**Decision.** Use the simplified Palmer penguins table (344 rows). It is released under CC0 1.0, is the standard
modern replacement for `iris` in teaching, and ships as a plain CSV, so both languages read the identical file.
The citation lives in `data/README.md`.

**Consequences.** No download step and no API key. The data is nearly separable by species, so the classifier
looks perfect; the README says that plainly. Alternatives considered: `iris` (licence and provenance are murkier),
scikit-learn's bundled sets (not available in R), downloading at build time (breaks offline runs and CI determinism).
