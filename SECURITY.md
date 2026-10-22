# Security policy

This is a reference project. It ships no credentials, calls no external API, and contains no real customer or
analytics data.

## Reporting a vulnerability

Do not open a public issue for a security problem. Use GitHub's private vulnerability reporting
(Security tab, "Report a vulnerability") on this repository. If that is unavailable, contact DCtech.
through https://dctech.live.

You can expect an acknowledgement within a few working days. This is a small project without a bounty program.

## Scope and design notes

- The marketing data is **synthetic** and generated from a seed. Hostnames use the reserved `example.test` domain;
  no e-mail addresses or personal identifiers are generated (a test asserts this).
- The dashboard is a static HTML file with no script and no external request; every dynamic string is escaped
  (a test injects markup to prove it).
- Do not point the pipeline at a real GA4 export without reviewing what personal data it contains
  (`user_pseudo_id`, `geo`, `device`). See the limitations in the README.
- CI runs gitleaks over the full git history on every push.
