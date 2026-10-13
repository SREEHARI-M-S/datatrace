# DataTrace

[![version](https://img.shields.io/badge/version-0.1.6-blue)](https://github.com/SREEHARI-M-S/datatrace/commits/main)

**Repository:** [github.com/SREEHARI-M-S/datatrace](https://github.com/SREEHARI-M-S/datatrace)  
**Latest on `main`:** [commit history](https://github.com/SREEHARI-M-S/datatrace/commits/main)

**Chrome DevTools for your data pipeline.**

DataTrace answers: *why did this specific value become what it is?* using
execution events and evidence-backed root-cause analysis.

## Boundary with ShadowFlow

- **ShadowFlow** — git revisions, historical replay, pre-merge impact.
- **DataTrace** — transformation events, production/debug forensics.

## Quick start

```bash
pip install -e ".[dev]"
datatrace --help
datatrace explain --record customer_id=183729
datatrace explain --record customer_id=183729 --store examples/sample_events.jsonl
datatrace stats
datatrace validate
datatrace records
datatrace explain --record customer_id=183729 -o forensics.md
datatrace datasets
datatrace ingest --file event.json --store events.jsonl
```

MIT License
