"""ARC research control: stdlib-only scoring, registry, reports and Git CAS claims."""
import argparse
import copy
import csv
import hashlib
import json
import math
import os
import re
from pathlib import Path
import statistics
import subprocess
import tempfile
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
STATE = "research/control/state.json"
CONTROL_BRANCH = "research/control-v2"
STATES = {"QUEUED", "CLAIMED", "RUNNING", "INFRA_ERROR", "WAITING_INPUT",
          "INCONCLUSIVE", "SCIENTIFIC_REJECT", "COMPLETE"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def finite(value, name):
    require(isinstance(value, (float, int)) and not isinstance(value, bool)
            and math.isfinite(value) and value >= 0, f"Invalid {name}: {value!r}")
    return value


def encoded(value):
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False) + "\n"


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def sha_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def score_record(record):
    """Failures require the actual official zero-prediction penalty, never drop rows."""
    panel = record["panel"]
    for field in ("dataset", "revision", "stage", "shape", "dtype", "evaluator", "meter"):
        require(panel.get(field) is not None, f"Panel missing {field}")
    require(panel["stage"] in {"development", "confirmation"}, "Invalid panel stage")
    rows = record["per_network"]
    require(bool(rows), "No network measurements")
    require(len(rows) == panel["count"], "Partial panel: row count differs")
    ids = [r["network_id"] for r in rows]
    require(all(isinstance(i, str) and i for i in ids), "Network IDs must be strings")
    require(len(set(ids)) == len(ids), "Duplicate network ID")
    scores = []
    for row in rows:
        require(isinstance(row.get("target_sha256"), str) and
                re.fullmatch(r"[0-9a-f]{64}", row["target_sha256"]), "Missing target fingerprint")
        mse = finite(row["final_mse"], "MSE")
        flops = finite(row["measured_flops"], "measured FLOPs")
        budget = finite(row["budget_flops"], "budget")
        require(budget > 0, "Budget must be positive")
        require(row["status"] in {"ok", "failed"}, "Unknown evaluation status")
        if row["status"] == "ok":
            require(flops <= budget, "Successful row exceeds official FLOP budget")
            score = mse * max(0.1, flops / budget)
        else:
            score = finite(row.get("official_adjusted_score"), "official failure score")
        if "official_adjusted_score" in row:
            require(math.isclose(score, row["official_adjusted_score"], rel_tol=1e-9,
                                 abs_tol=1e-18), "Score disagrees with official report")
        scores.append(score)
    return {"adjusted_score": statistics.mean(scores),
            "raw_mse": statistics.mean(r["final_mse"] for r in rows),
            "mean_measured_flops": statistics.mean(r["measured_flops"] for r in rows),
            "failures": sum(r["status"] == "failed" for r in rows), "scores": scores}


def panel_key(record):
    score_record(record)
    p = record["panel"]
    return encoded({"panel": p, "networks": sorted(
        (r["network_id"], r["target_sha256"], r["budget_flops"])
        for r in record["per_network"])})


def compare(candidate, parent):
    require(panel_key(candidate) == panel_key(parent), "NOT_COMPARABLE: panels differ")
    a, b = score_record(candidate), score_record(parent)
    by_id = dict(zip((r["network_id"] for r in parent["per_network"]), b["scores"]))
    deltas = [by_id[r["network_id"]] - s
              for r, s in zip(candidate["per_network"], a["scores"])]
    n = len(deltas)
    return {"candidate": candidate["id"], "parent": parent["id"], "networks": n,
            "score_ratio": a["adjusted_score"] / b["adjusted_score"]
            if b["adjusted_score"] else None,
            "paired_gain_mean": statistics.mean(deltas),
            "paired_gain_se": statistics.stdev(deltas) / math.sqrt(n) if n > 1 else None,
            "improved_networks": sum(d > 0 for d in deltas),
            "worst_score_degradation": max(-d for d in deltas),
            "interpretation": "SE across networks; not a significance or holdout claim"}


def validate_state(state):
    require(state["schema_version"] == 2, "Unsupported control schema")
    ids = [j["id"] for j in state["jobs"]]
    require(len(ids) == len(set(ids)), "Duplicate job ID")
    jobs = {j["id"]: j for j in state["jobs"]}
    run_ids = []
    for job in jobs.values():
        require(isinstance(job["id"], str) and re.fullmatch(r"[A-Za-z][A-Za-z0-9_-]*", job["id"]),
                "Invalid job ID")
        require(job["status"] in STATES, "Unknown job status")
        require(all(d in jobs and d != job["id"] for d in job["depends_on"]),
                "Invalid dependency")
        if job["status"] in {"CLAIMED", "RUNNING"}:
            require(bool(job.get("owner")), "Owned state without owner")
        for attempt in job.get("attempts", []):
            require(isinstance(attempt["run_id"], str), "Run IDs must be strings")
            run_ids.append(attempt["run_id"])
    require(len(run_ids) == len(set(run_ids)), "Run ID used twice")
    def visit(key, chain):
        require(key not in chain, "Dependency cycle")
        for dep in jobs[key]["depends_on"]:
            visit(dep, chain | {key})
    for key in jobs:
        visit(key, set())
    return state


def update(state, action, job_id, owner, payload=None):
    state = copy.deepcopy(validate_state(state))
    jobs = {j["id"]: j for j in state["jobs"]}
    payload = payload or {}
    require(bool(owner), "Owner required")
    if action == "enqueue":
        require(owner == state.get("coordinator_key", "coordinator"), "Coordinator only")
        require(job_id not in jobs, "Job ID already allocated")
        require(all(payload.get(k) is not None for k in
                    ("title", "hypothesis_id", "priority", "deliverable", "depends_on")),
                "Incomplete job definition")
        state["jobs"].append({**payload, "id": job_id, "owner": None,
                              "status": "QUEUED", "attempts": []})
        job = state["jobs"][-1]
    else:
        require(job_id in jobs, "Unknown job")
        job = jobs[job_id]
    if action == "enqueue":
        pass
    elif action == "claim":
        require(job.get("assigned_owner") in {None, owner}, "Different assigned owner")
        if job["status"] in {"CLAIMED", "RUNNING"} and job.get("owner") == owner:
            return state  # delivery retry is idempotent
        require(job["status"] in {"QUEUED", "WAITING_INPUT"}, "Job is not claimable")
        require(all(jobs[d]["status"] == "COMPLETE" and jobs[d].get("receipt")
                    for d in job["depends_on"]), "WAITING_INPUT: dependency not complete")
        require(job.get("owner") in {None, owner}, "Job belongs to another owner")
        job.update(status="CLAIMED", owner=owner)
    else:
        require(job.get("owner") == owner, "Owner mismatch")
        if action == "start":
            run_id = payload.get("run_id")
            require(isinstance(run_id, str) and bool(run_id), "run_id required")
            if job["status"] == "RUNNING" and job["attempts"][-1]["run_id"] == run_id:
                require(all(job["attempts"][-1].get(k) == v for k, v in payload.items()),
                        "Repeated start changed run metadata")
                return state
            require(job["status"] == "CLAIMED", "Claim before starting")
            require(payload.get("code_commit") and payload.get("command"),
                    "Record code commit and executable command before launch")
            job.setdefault("attempts", []).append({**payload, "status": "RUNNING"})
            job["status"] = "RUNNING"
        elif action == "finish":
            require(job["status"] in {"CLAIMED", "RUNNING"}, "Job is not active")
            require(payload.get("status") in {"COMPLETE", "INFRA_ERROR", "INCONCLUSIVE",
                                               "SCIENTIFIC_REJECT", "WAITING_INPUT"},
                    "Invalid finish status")
            receipt = payload.get("receipt", {})
            require(receipt.get("url") and re.fullmatch(r"[0-9a-f]{64}", receipt.get("sha256", "")),
                    "Durable receipt URL and SHA256 required")
            require(payload.get("reason"), "Reason required")
            job.update(status=payload["status"], receipt=receipt, reason=payload["reason"])
            if job.get("attempts"):
                job["attempts"][-1]["status"] = payload["status"]
        elif action == "repair":
            require(job["status"] == "INFRA_ERROR", "Only infrastructure repair uses repair")
            require(payload.get("reason"), "Repair explanation required")
            job.update(status="CLAIMED", reason=payload["reason"])
        else:
            raise ValueError("Unknown action")
    state["revision"] += 1
    state.setdefault("events", []).append({"revision": state["revision"], "action": action,
        "job": job_id, "owner": owner, "payload": payload,
        "at": datetime.now(timezone.utc).isoformat()})
    return validate_state(state)


def git(*args, data=None, env=None):
    result = subprocess.run(["git", *args], cwd=ROOT, input=data, capture_output=True,
                            encoding="utf-8", env=env)
    if result.returncode:
        raise RuntimeError(result.stderr.strip())
    return result.stdout.strip()


def publish(action, job_id, owner, payload):
    """Non-fast-forward push rejects a race; no force push or implicit retry."""
    git("fetch", "origin", CONTROL_BRANCH)
    base = git("rev-parse", "FETCH_HEAD")
    state = json.loads(git("show", f"{base}:{STATE}"))
    revised = update(state, action, job_id, owner, payload)
    if revised == state:
        return {"commit": base, "idempotent": True}
    paths = git("ls-tree", "-r", "--name-only", base, "--", "research/results").splitlines()
    data = [json.loads(git("show", f"{base}:{p}")) for p in paths if p.endswith(".json")]
    history = json.loads(git("show", f"{base}:research/history.json"))
    files = {STATE: encoded(revised), "research/control/STATUS.md": report(revised, data, history)}
    with tempfile.TemporaryDirectory(prefix="arc-index-") as directory:
        env = {**os.environ, "GIT_INDEX_FILE": str(Path(directory) / "index")}
        git("read-tree", base, env=env)
        for path, content in files.items():
            blob = git("hash-object", "-w", "--stdin", data=content)
            git("update-index", "--add", "--cacheinfo", f"100644,{blob},{path}", env=env)
        tree = git("write-tree", env=env)
        commit = git("commit-tree", tree, "-p", base,
                     data=f"control: {action} {job_id} by {owner}\n")
    git("push", "origin", f"{commit}:refs/heads/{CONTROL_BRANCH}")
    return {"commit": commit, "revision": revised["revision"], "idempotent": False}


def records():
    return [load(p) for p in sorted((ROOT / "research/results").glob("*.json"))]


def esc(value):
    return str(value).replace("|", "\\|").replace("\n", " ")


def report(state, data, history):
    validate_state(state)
    lines = ["# ARC — исследования и результаты", "",
             "Generated by scripts/arc_control.py report. Низкий adjusted score лучше.", "",
             "Очередь ниже — снимок. Живые назначения: [control branch](https://github.com/tim8es/arc-whitebox/blob/research/control-v2/research/control/state.json).",
             "Проверить актуальный статус: `python scripts/arc_control.py status --remote`.", "",
             "## Измеренные сопоставимые результаты", "",
             "Это только нормализованные результаты с полными строками по сетям; не весь исторический frontier.",
             "Пять сетей E173 — development-проверка, а не полный mini и не официальное место.", "",
             "| Результат | Сетей | Raw MSE | Adjusted score | Измеренные FLOPs/сеть | Сбои | Evidence |",
             "|---|---:|---:|---:|---:|---:|---|"]
    groups = {}
    for record in data:
        result = score_record(record)
        groups.setdefault(panel_key(record), []).append(record)
        lines.append(f"| {esc(record['id'])} | {len(record['per_network'])} | {result['raw_mse']:.8g} | "
                     f"{result['adjusted_score']:.8g} | {result['mean_measured_flops']:.0f} | "
                     f"{result['failures']} | [{esc(record['evidence_level'])}]({record['receipt_url']}) |")
    lines += ["", "### Сравнения внутри одинаковых панелей", ""]
    for n, group in enumerate(groups.values(), 1):
        best = min(group, key=lambda r: score_record(r)["adjusted_score"])
        lines.append(f"Панель {n}: лучший среди загруженных сопоставимых записей — {best['id']}.")
        by_id = {r["id"]: r for r in group}
        for item in group:
            if item.get("parent_id") in by_id:
                cmp = compare(item, by_id[item["parent_id"]])
                ratio = cmp["score_ratio"]
                lines.append(f"- {item['id']} / {item['parent_id']}: {ratio:.8f}; "
                             f"улучшение {(1-ratio)*100:.4f}%; "
                             f"{cmp['improved_networks']}/{cmp['networks']} сетей.")
        lines.append("")
    lines += ["## Очередь работ", "", "| ID | Приоритет | Работа | Статус | Исполнитель | Зависит от |",
              "|---|---:|---|---|---|---|"]
    for job in sorted(state["jobs"], key=lambda j: (j["priority"], j["id"])):
        lines.append("| " + " | ".join(esc(v) for v in [job["id"], job["priority"], job["title"],
            job["status"], job.get("owner") or job.get("assigned_owner") or "—",
            ", ".join(job["depends_on"]) or "—"]) + " |")
    entries = history.get("experiments", [])
    lines += ["", "## Исторический индекс", "",
              f"Учтено {len(entries)} номеров; артефактов {sum(len(e['artifacts']) for e in entries)}; "
              f"без найденных источников {sum(e['coverage'] == 'MISSING' for e in entries)}.", "",
              "Архивные решения сохранены дословно; их наличие не означает современную независимую верификацию.",
              "Пропуски отмечены явно. Исторические числа из свободного текста автоматически не ранжируются.", "",
              "| ID | Тема | Покрытие | Артефактов | Пример источника |", "|---|---|---|---:|---|"]
    for entry in entries:
        artifacts = entry["artifacts"]
        source = f"[source]({artifacts[0]['url']})" if artifacts else "—"
        lines.append(f"| {entry['experiment_id']} | {esc(entry['title'])} | {esc(entry['coverage'])} | {len(artifacts)} | {source} |")
    lines += ["", "Полные ссылки, варианты веток и старые решения: [history.json](../history.json).",
              "Таблица для фильтрации: [history.csv](../history.csv). Старый реестр: [legacy-ledger.csv](../legacy-ledger.csv).",
              "Правила работы: [RESEARCH_PROCESS.md](../RESEARCH_PROCESS.md).", ""]
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("check")
    sub.add_parser("report")
    status = sub.add_parser("status")
    status.add_argument("--remote", action="store_true")
    comp = sub.add_parser("compare")
    comp.add_argument("candidate")
    comp.add_argument("parent")
    for name in ("claim", "start", "finish", "repair", "enqueue"):
        p = sub.add_parser(name)
        p.add_argument("job")
        p.add_argument("--owner", required=True)
        p.add_argument("--payload", type=Path)
        p.add_argument("--publish", action="store_true", help="Atomic remote update; required for execution")
    args = parser.parse_args()
    if args.command == "compare":
        print(encoded(compare(load(args.candidate), load(args.parent))))
        return
    state = load(ROOT / STATE)
    if args.command == "status":
        if args.remote:
            git("fetch", "origin", CONTROL_BRANCH)
            state = json.loads(git("show", f"FETCH_HEAD:{STATE}"))
        validate_state(state)
        print(encoded(state))
    elif args.command in {"check", "report"}:
        validate_state(state)
        data = records()
        for record in data:
            score_record(record)
        require(len({r["id"] for r in data}) == len(data), "Duplicate result ID")
        history = load(ROOT / "research/history.json")
        output = report(state, data, history)
        target = ROOT / "research/control/STATUS.md"
        if args.command == "report":
            target.write_text(output, encoding="utf-8")
            with (ROOT / "research/history.csv").open("w", encoding="utf-8-sig", newline="") as stream:
                writer = csv.writer(stream)
                writer.writerow(["experiment_id", "title", "coverage", "artifact_count",
                                 "declared_historical_statuses", "source"])
                for item in history["experiments"]:
                    artifacts = item["artifacts"]
                    writer.writerow([item["experiment_id"], item["title"], item["coverage"], len(artifacts),
                        "; ".join(sorted({a["declared_status"] for a in artifacts if a["declared_status"]})),
                        artifacts[0]["url"] if artifacts else ""])
        else:
            require(target.read_text(encoding="utf-8") == output, "Report stale: run report")
            print(f"PASS: {len(data)} normalized results, {len(state['jobs'])} jobs, "
                  f"{len(history['experiments'])} history entries")
    else:
        payload = load(args.payload) if args.payload else {}
        if args.publish:
            print(encoded(publish(args.command, args.job, args.owner, payload)))
        else:
            print(encoded(update(state, args.command, args.job, args.owner, payload)))
            print("DRY RUN only: no ownership acquired; execution requires --publish")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, KeyError, RuntimeError, OSError) as exc:
        raise SystemExit(f"ARC control error: {exc}") from exc
