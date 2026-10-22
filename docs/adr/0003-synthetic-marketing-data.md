# 0003: Synthetic marketing data, standard library only

**Status:** accepted

**Context.** The marketing pipeline must be demonstrable without any real client site, GA4 property or ad account,
and without personal data.

**Decision.** A seeded generator (`random.Random(seed)`) emits invented traffic on the reserved `example.test` domain
in the shape of the documented GA4 BigQuery export (`events_YYYYMMDD`, repeated `event_params`, nested `device`,
`geo`, `traffic_source`, `ecommerce`), a Search Console CSV and an Ads CSV. The package has no runtime dependencies.
The generated files (about 25 MB) are git-ignored; the seed recreates them.

**Consequences.** Same seed, same data, so tests are exact and the dashboard is reproducible. The generator is
internally consistent on purpose (organic sessions follow Search Console clicks; paid clicks follow GA sessions) so the
reconciliation logic has something to check, but it cannot reproduce real-world messiness; the README lists this.
