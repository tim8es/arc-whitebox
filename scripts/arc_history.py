"""Offline inventory of research/docs evidence reachable from local origin refs.

Includes old versions and deleted files in reachable commits. Artifact refs mean
the branches whose history contains that exact experiment/path/blob, not just
branches containing it at their tips. The lexicographically smallest containing
commit supplies the immutable URL. Symbolic origin/HEAD is not a separate source.

Coverage is ARTIFACTS, LEGACY_ONLY, or MISSING; it is not a scientific verdict.
Legacy CSV fields remain strings, including free-text metrics. Only top-level
JSON status (or decision if status is absent/null) supplies declared_status.
Other payloads, including vectors, are indexed but never copied or parsed.
"""

import argparse
from concurrent.futures import ThreadPoolExecutor
import csv
import io
import json
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
from urllib.parse import quote, urlsplit


EXPERIMENT = re.compile(r"E[0-9]{3}(?![0-9])", re.IGNORECASE)
JSON_LIMIT = 1024 * 1024
LEDGER_LIMIT = 8 * 1024 * 1024
BOOTSTRAP = "refs/remotes/origin/research/bootstrap"


def git(repo, *args):
    result = subprocess.run(
        ["git", *args], cwd=repo, env={**os.environ, "GIT_NO_LAZY_FETCH": "1"},
        capture_output=True, check=False,
    )
    if result.returncode:
        raise RuntimeError(
            f"git {' '.join(args)} failed: {result.stderr.decode('utf-8', 'replace').strip()}. "
            "Automatic fetching is disabled; explicitly fetch missing objects or use "
            "a full clone, then rerun python scripts/arc_history.py refresh."
        )
    return result.stdout


def source_base(repo):
    remote = git(repo, "remote", "get-url", "origin").decode().strip()
    if re.match(r"[^/@]+@[^/:]+:", remote):
        host, path = remote.split("@", 1)[1].split(":", 1)
        remote = f"https://{host}/{path}"
    parsed = urlsplit(remote)
    if parsed.scheme not in {"https", "http", "ssh"} or not parsed.hostname:
        raise RuntimeError("origin must have an HTTP(S) or SSH URL for immutable source links.")
    scheme = "https" if parsed.scheme == "ssh" else parsed.scheme
    host = parsed.hostname
    if parsed.port and parsed.scheme != "ssh":
        host += f":{parsed.port}"
    return f"{scheme}://{host}{parsed.path.rstrip('/').removesuffix('.git')}"


def read_blobs(repo, blobs, json_blobs, ledger_blob):
    """Check every indexed blob; read only bounded JSON and the legacy CSV.

    One cat-file process services both size checks and content requests, so large
    vectors never enter Python memory. Missing objects fail before output writes.
    """
    statuses = {}
    legacy = None
    missing = []
    with subprocess.Popen(
        ["git", "cat-file", "--batch-command"], cwd=repo,
        env={**os.environ, "GIT_NO_LAZY_FETCH": "1"},
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
    ) as batch:
        try:
            for blob in sorted(blobs):
                batch.stdin.write(f"info {blob}\n".encode())
                batch.stdin.flush()
                header = batch.stdout.readline().split()
                if len(header) == 2 and header[1] == b"missing":
                    missing.append(f"{blob} ({blobs[blob]})")
                    continue
                if len(header) != 3 or header[1] != b"blob":
                    raise RuntimeError(f"Cannot inspect local blob {blob}; check local Git objects.")
                size = int(header[2])
                if blob == ledger_blob and size > LEDGER_LIMIT:
                    raise RuntimeError(f"Legacy ledger exceeds the {LEDGER_LIMIT}-byte parsing limit.")
                if blob != ledger_blob and (blob not in json_blobs or size > JSON_LIMIT):
                    continue
                batch.stdin.write(f"contents {blob}\n".encode())
                batch.stdin.flush()
                content_header = batch.stdout.readline().split()
                if content_header != header:
                    raise RuntimeError(f"Blob {blob} became unavailable while reading; rerun after repair.")
                payload = batch.stdout.read(size)
                if len(payload) != size or batch.stdout.read(1) != b"\n":
                    raise RuntimeError(f"Incomplete local blob {blob}; repair the clone and rerun.")
                if blob == ledger_blob:
                    legacy = payload
                if blob in json_blobs and size <= JSON_LIMIT:
                    try:
                        value = json.loads(payload)
                    except (ValueError, UnicodeError, RecursionError):
                        continue
                    if isinstance(value, dict):
                        status = value.get("status")
                        if status is None:
                            status = value.get("decision")
                        # Keep literal declarations, never interpret filenames or metrics.
                        if isinstance(status, str):
                            statuses[blob] = status
        finally:
            batch.stdin.close()
            batch.wait()
    if missing:
        raise RuntimeError(
            f"{len(missing)} missing local blob(s): " + "; ".join(missing[:10])
            + ". Explicitly fetch the missing objects (e.g. git fetch origin <blob>) "
            "or use a full clone, then rerun python scripts/arc_history.py refresh. "
            "GIT_NO_LAZY_FETCH=1; no network fetch was attempted."
        )
    if legacy is None:
        raise RuntimeError("Legacy ledger could not be read from the local bootstrap commit.")
    return statuses, legacy


def build_inventory(repo):
    base = source_base(repo)
    refs = []
    for line in git(repo, "for-each-ref", "--format=%(refname) %(objectname) %(symref)",
                    "refs/remotes/origin/").decode().splitlines():
        fields = line.split()
        if len(fields) == 2:
            refs.append({"ref": fields[0], "commit": fields[1]})
    refs.sort(key=lambda item: item["ref"])
    tips = {item["ref"]: item["commit"] for item in refs}
    if BOOTSTRAP not in tips:
        raise RuntimeError(f"Missing local {BOOTSTRAP}; fetch that branch explicitly and rerun.")

    # Snapshot all tip SHAs once; subsequent commands never depend on moving refs.
    graph = [line.split() for line in git(
        repo, "rev-list", "--topo-order", "--parents", *sorted(set(tips.values()))
    ).decode().splitlines()]
    reachable = {}
    for ref, commit in tips.items():
        reachable.setdefault(commit, set()).add(ref)
    for commit, *parents in graph:
        for parent in parents:
            reachable.setdefault(parent, set()).update(reachable[commit])

    def tree(commit):
        return commit, git(repo, "ls-tree", "-r", "-z", commit, "--", "research", "docs")

    artifacts = {}
    blobs = {}
    json_blobs = set()
    ledger_blob = None
    # Bounded parallel metadata reads; content reads still use one cat-file batch.
    with ThreadPoolExecutor(max_workers=4) as workers:
        for commit, listing in workers.map(tree, sorted(reachable)):
            for record in listing.split(b"\0"):
                if not record:
                    continue
                metadata, raw_path = record.split(b"\t", 1)
                _, kind, raw_blob = metadata.split()
                if kind != b"blob":
                    continue
                path = raw_path.decode("utf-8", "surrogateescape")
                blob = raw_blob.decode("ascii")
                if commit == tips[BOOTSTRAP] and path == "research/ledger.csv":
                    ledger_blob = blob
                    blobs[blob] = path
                filename = PurePosixPath(path)
                ids = sorted(set(match.upper() for match in EXPERIMENT.findall(filename.name)))
                if not ids:
                    continue
                blobs.setdefault(blob, path)
                suffix = filename.suffix.lower()
                if suffix == ".json":
                    json_blobs.add(blob)
                for experiment_id in ids:
                    key = (experiment_id, path, blob)
                    if key not in artifacts:
                        artifacts[key] = {
                            "path": path, "blob": blob, "commit": commit,
                            "url": f"{base}/blob/{commit}/{quote(path, safe='/', errors='surrogatepass')}",
                            "refs": set(), "kind": suffix.lstrip(".") or "file",
                            "declared_status": None,
                        }
                    artifacts[key]["refs"].update(reachable[commit])
    if ledger_blob is None:
        raise RuntimeError(f"research/ledger.csv is absent from {BOOTSTRAP}.")
    statuses, legacy = read_blobs(repo, blobs, json_blobs, ledger_blob)
    rows_by_id = {}
    try:
        reader = csv.DictReader(io.StringIO(legacy.decode("utf-8-sig"), newline=""), strict=True)
        if not reader.fieldnames or "id" not in reader.fieldnames:
            raise ValueError("CSV requires an id column")
        for row in reader:
            if None in row or any(value is None for value in row.values()):
                raise ValueError("CSV row does not match the header")
            experiment_id = row["id"].strip().upper()
            if EXPERIMENT.fullmatch(experiment_id):
                rows_by_id.setdefault(experiment_id, []).append(row)
    except (UnicodeError, ValueError, csv.Error) as error:
        raise RuntimeError(f"Cannot parse legacy CSV: {error}") from error

    by_id = {}
    for (experiment_id, _, _), artifact in sorted(artifacts.items()):
        artifact["refs"] = sorted(artifact["refs"])
        if artifact["kind"] == "json":
            artifact["declared_status"] = statuses.get(artifact["blob"])
        by_id.setdefault(experiment_id, []).append(artifact)
    maximum = max([193] + [int(key[1:]) for key in by_id.keys() | rows_by_id.keys()])
    experiments = []
    for number in range(maximum + 1):
        experiment_id = f"E{number:03d}"
        evidence = by_id.get(experiment_id, [])
        rows = rows_by_id.get(experiment_id, [])
        title = experiment_id
        if evidence:
            preferred = min(evidence, key=lambda item: (item["kind"] != "md", item["path"]))
            title = re.sub(r"[_-]+", " ", PurePosixPath(preferred["path"]).stem)
        experiments.append({
            "experiment_id": experiment_id, "title": title,
            "coverage": "ARTIFACTS" if evidence else "LEGACY_ONLY" if rows else "MISSING",
            "legacy_rows": rows, "artifacts": evidence,
        })
    return {"schema_version": 1, "generated_from": refs, "experiments": experiments}, legacy


def refresh(repo):
    inventory, legacy = build_inventory(repo)
    # Serialize fully before writing; inspection/parsing failures preserve outputs.
    encoded = (json.dumps(inventory, indent=2, sort_keys=True, ensure_ascii=True,
                          allow_nan=False) + "\n").encode("utf-8")
    destination = Path(repo) / "research"
    destination.mkdir(exist_ok=True)
    (destination / "history.json").write_bytes(encoded)
    (destination / "legacy-ledger.csv").write_bytes(legacy)
    experiments = inventory["experiments"]
    gaps = [item["experiment_id"] for item in experiments if item["coverage"] == "MISSING"]
    print(f"{len(inventory['generated_from'])} refs; {len(experiments)} experiments; "
          f"{sum(len(item['artifacts']) for item in experiments)} artifact entries; "
          f"{sum(len(item['legacy_rows']) for item in experiments)} legacy rows")
    print("MISSING: " + (", ".join(gaps) or "none"))
    return inventory


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["refresh"])
    parser.parse_args()
    try:
        refresh(Path(__file__).resolve().parents[1])
    except (RuntimeError, OSError) as error:
        print(f"arc_history: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
