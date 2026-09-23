# Offline workflow preflight

Before arming an Actions workflow that reconstructs a runtime fixture manifest, run:

```bash
python scripts/arc_workflow_preflight.py \
  --workflow .github/workflows/<workflow>.yml \
  --fixture-generator research/<path>/<fixture_generator>.py
```

The command is standard-library only and performs static checks. It does **not** execute
the workflow, fixture generator, estimator, or competition data.

It fails closed when it cannot prove the supported contracts:

- every `git merge-base --is-ancestor` guard has a preceding
  `actions/checkout` whose own `with:` block contains `fetch-depth: 0` in the same job;
- runtime-manifest filenames referenced by the workflow match the generator output;
- the generator manifest object uses only statically modeled mutations before serialization;
- `json.loads` reads the exact runtime-manifest path, and workflow manifest accesses use
  statically verifiable bracket-key paths present in the object traced to the generator's
  `json.dumps(...)` runtime-manifest write.

Run the focused regression suite with:

```bash
python -m unittest tests/test_arc_workflow_preflight.py -v
```
