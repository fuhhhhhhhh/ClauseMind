# Third-Party Source

This directory stores third-party source code vendored for local inspection and integration.

## MinerU

`third_party/MinerU` was copied from a local editable MinerU checkout for
inspection and integration inside ClauseMind. Keep machine-specific source paths
out of committed docs; use the relative vendored path in this repository.

Source metadata at copy time:

```text
branch: test
commit: 257f7b580053a2e9a4ccac64db9128e49446c195
```

Installed package metadata reported:

```text
name: mineru
version: 3.1.9
```

Do not modify external MinerU checkouts or existing conda environments when
working on ClauseMind. If ClauseMind needs local source changes, edit the
vendored copy here or create a separate environment.
