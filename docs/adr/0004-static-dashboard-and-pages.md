# 0004: Static dashboard, no scripts, Pages only when public

**Status:** accepted

**Context.** The dashboard should be viewable anywhere, including as a CI artifact, without a server, a JavaScript
dependency or an external request. Publishing demos is an owner decision.

**Decision.** `ga4-synth report` writes one self-contained HTML file: inline CSS, inline SVG charts, every chart backed
by a table, light and dark themes, a permanent "synthetic data" banner. The Pages workflow builds this plus the Quarto
report, but its job is conditioned on `github.event.repository.private == false`, so it does nothing while the
repository is private. GitHub Pages is the only demo target; no other hosting is used.

**Consequences.** Nothing can phone home and nothing needs a CDN. Interactivity (filters, tooltips) is out of scope.
After the owner makes the repository public, enabling Pages (Settings, Pages, source "GitHub Actions") is the only
step left.
