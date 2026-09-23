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

- ancestry guards are recognized with supported shell whitespace/line continuations, and every guard has a preceding structural workflow step using `actions/checkout` whose own `with:` mapping contains `fetch-depth: 0` in the same job; block-scalar/comment text cannot supply checkout metadata;
- runtime-manifest filenames referenced by the workflow match the generator output;
- the generator manifest object uses only statically modeled assignments/updates before serialization; unsupported control flow, deletion, mutation, helper flow, or write reachability fails closed;
- `json.loads` reads the exact runtime-manifest path from a supported `run: |` Python verifier slice, and AST-parsed manifest accesses exclude comments/string literals, require literal bracket-key paths, and reject aliasing, dynamic subscripts, method calls, helper passing, or other unmodeled uses;
- every asserted key path is present in the object traced to the generator's `json.dumps(...)` runtime-manifest write.

Run the focused regression suite with:

```bash
python -m unittest tests/test_arc_workflow_preflight.py -v
```
