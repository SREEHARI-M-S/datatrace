# DataTrace

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
datatrace explain --record customer_id=183729 --store ./events.jsonl
```

MIT License
