#!/usr/bin/env python3
"""
AIS Orchestrator — Hermes als AIS-Steuerzentrale
================================================
Läuft auf dem Pi (immer an) und koordiniert Issue-Solving
über Metis-Cluster-Worker und externe Modelle.

Workflow:
  1. Lies offene Issues vom Smart-Home Repo
  2. Prüfe welche Issues "solver"-markiert sind
  3. Wähle Worker/Modell basierend auf Issue-Typ und Verfügbarkeit
  4. Starte solve_issues.py auf dem besten verfügbaren Worker
  5. Berichte Ergebnis an Hermes → Telegram

Usage:
  python3 ais_orchestrate.py --list-issues
  python3 ais_orchestrate.py --solve-issue 1
  python3 ais_orchestrate.py --dispatch-all
  python3 ais_orchestrate.py --status
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional

# Metis paths
METIS_ROOT = Path.home() / "metis"
AIS_ROOT = Path.home() / "ais-orchestrator"
SMARTHOME_ROOT = Path.home() / "smarthome"

# ─── SSH-Wrapper für iMac2 Token ────────────────────────────────────────────

IMAC2 = "Guido@192.168.178.43"
SSH_KEY = os.path.expanduser("~/.ssh/metis_ed25519")


def get_github_token() -> str:
    """Holt GitHub OAuth Token vom iMac2 via SSH."""
    cmd = [
        "ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=8",
        "-i", SSH_KEY, IMAC2,
        "python3 -c \"import re; t=open('$HOME/.config/gh/hosts.yml').read(); print(re.search(r'oauth_token:\\s*(\\S+)', t).group(1))\""
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return result.stdout.strip()


def github_api(url: str, token: str, method: str = "GET", data: Optional[dict] = None) -> dict:
    """Macht einen GitHub API Call."""
    import urllib.request, urllib.error
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    body = json.dumps(data).encode() if data else None
    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


# ─── Issue Modell ─────────────────────────────────────────────────────────────

@dataclass
class Issue:
    number: int
    title: str
    body: str
    labels: list[str]
    state: str
    assignee: Optional[str]
    created_at: str
    updated_at: str

    @property
    def is_solver_ready(self) -> bool:
        return "state/ready" in self.labels or "state/backlog" in self.labels

    @property
    def is_solver_marked(self) -> bool:
        return "agent/solver" in self.labels or "kind/feature" in self.labels or "kind/automation" in self.labels

    @property
    def is_human_only(self) -> bool:
        return "agent/human" in self.labels

    @property
    def area(self) -> Optional[str]:
        for label in self.labels:
            if label.startswith("area/"):
                return label
        return None

    @property
    def needs_node_red(self) -> bool:
        return self.area == "area/node-red" or "node-red" in self.body.lower()


# ─── Worker-Auswahl ─────────────────────────────────────────────────────────

@dataclass
class WorkerStatus:
    id: str
    role: str
    reachable: bool
    status: str
    temperature_c: Optional[float]
    notes: str = ""


def get_worker_status() -> list[WorkerStatus]:
    """Liest Worker-Status aus dem Metis Health-Check."""
    import yaml
    health_script = METIS_ROOT / "scripts" / "healthcheck_workers.py"
    if not health_script.exists():
        return []

    result = subprocess.run(
        [sys.executable, str(health_script), "--include-non-workers", "--json"],
        capture_output=True, text=True, cwd=str(METIS_ROOT)
    )
    if result.returncode != 0:
        return []

    data = json.loads(result.stdout)
    workers = []
    for w in data:
        workers.append(WorkerStatus(
            id=w["worker_id"],
            role=w.get("role", ""),
            reachable=w.get("reachable", False),
            status=w.get("status", "unknown"),
            temperature_c=w.get("max_temperature_c")
        ))
    return workers


def best_worker_for_issue(issue: Issue, workers: list[WorkerStatus]) -> Optional[WorkerStatus]:
    """Wählt den besten Worker für ein Issue."""
    candidates = [w for w in workers if w.reachable and w.status in ("ok", "ready")]

    # mac-imac-2 ist immer bevorzugt wenn erreichbar (stärkster Worker)
    for w in candidates:
        if w.id == "mac-imac-2":
            return w

    # Dann linux-laptop-2 (bester local-model Kandidat)
    for w in candidates:
        if w.id == "linux-laptop-2":
            return w

    # gaming-pc falls reachable
    for w in candidates:
        if w.id == "gaming-pc":
            return w

    # Fallback: control-plane selbst (aber nur für low-risk)
    for w in candidates:
        if w.id == "raspberry-control-plane" and not issue.needs_node_red:
            return w

    return None


# ─── Issue Management ────────────────────────────────────────────────────────

def list_open_issues(token: str, repo: str = "SaJaToGu/smarthome") -> list[Issue]:
    """Listet alle offenen Issues vom Repo."""
    issues = []
    page = 1
    while True:
        data = github_api(
            f"https://api.github.com/repos/{repo}/issues?state=open&per_page=50&page={page}",
            token
        )
        if not data:
            break
        for item in data:
            if "pull_request" in item:
                continue
            issues.append(Issue(
                number=item["number"],
                title=item["title"],
                body=item.get("body", ""),
                labels=[l["name"] for l in item.get("labels", [])],
                state=item["state"],
                assignee=(item.get("assignee") or {}).get("login"),
                created_at=item["created_at"],
                updated_at=item["updated_at"]
            ))
        if len(data) < 50:
            break
        page += 1
    return issues


def update_issue_label(token: str, issue_nr: int, label: str, action: str, repo: str = "SaJaToGu/smarthome"):
    """Fügt hinzu oder entfernt ein Label von einem Issue."""
    url = f"https://api.github.com/repos/{repo}/issues/{issue_nr}/labels"
    if action == "add":
        github_api(url, token, method="POST", data={"labels": [label]})
    elif action == "remove":
        # DELETE /repos/{owner}/{repo}/issues/{issue_number}/labels/{name}
        from urllib.error import HTTPError
        try:
            github_api(f"{url}/{label}", token, method="DELETE")
        except HTTPError as e:
            if e.code != 404:
                raise


def add_comment(token: str, issue_nr: int, body: str, repo: str = "SaJaToGu/smarthome"):
    """Fügt einen Kommentar zu einem Issue hinzu."""
    github_api(
        f"https://api.github.com/repos/{repo}/issues/{issue_nr}/comments",
        token, method="POST", data={"body": body}
    )


# ─── Solver Dispatch ─────────────────────────────────────────────────────────

def dispatch_solve(
    issue: Issue,
    token: str,
    model: Optional[str] = None,
    dry_run: bool = False
) -> dict:
    """
    Startet den AIS Solver für ein einzelnes Issue.
    Nutzt den Pi als lokalen Worker (python scripts/solve_issues.py).
    """
    repo = "SaJaToGu/smarthome"

    # Labeln: state/in-progress
    update_issue_label(token, issue.number, "state/in-progress", "add", repo)

    comment = (
        f"🚀 **AIS Solver gestartet**\n"
        f"- Issue: #{issue.number} — {issue.title}\n"
        f"- Zeit: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"- Modell: {model or 'default (minimax/minimax-m3)'}\n"
        f"- Worker: raspberry-control-plane (local)"
    )
    add_comment(token, issue.number, comment, repo)

    if dry_run:
        return {"status": "dry-run", "issue": issue.number, "model": model}

    # Fork & Solve auf Smart-Home Repo
    # 1. Fork erstellen falls nötig
    # 2. solve_issues.py mit issue nummer
    cmd = [
        sys.executable,
        str(AIS_ROOT / "scripts" / "solve_issues.py"),
        "--model", "openrouter",
        "--model-name", model or "minimax/minimax-m3",
        "--repo", repo,
        "--issue", str(issue.number),
        "--openrouter-api-key", os.environ.get("OPENROUTER_API_KEY", ""),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=str(AIS_ROOT))

    if result.returncode != 0:
        update_issue_label(token, issue.number, "state/blocked", "add", repo)
        add_comment(token, issue.number, f"❌ **Solver fehlgeschlagen**\n```\n{result.stderr[-1000:]}\n```", repo)
        return {"status": "error", "issue": issue.number, "stderr": result.stderr[-500:]}

    update_issue_label(token, issue.number, "state/done", "add", repo)
    add_comment(token, issue.number, f"✅ **Solver abgeschlossen** — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", repo)
    return {"status": "ok", "issue": issue.number, "stdout": result.stdout[-500:]}


# ─── Kommandozeilen Interface ────────────────────────────────────────────────

def cmd_list(args) -> None:
    token = get_github_token()
    issues = list_open_issues(token)
    print(f"\n{'#':<4} {'State':<14} {'Area':<16} {'Agent':<14} {'Title'}")
    print("-" * 100)
    for issue in sorted(issues, key=lambda i: i.number):
        state = next((l for l in issue.labels if l.startswith("state/")), "")
        area = issue.area or ""
        agent = next((l for l in issue.labels if l.startswith("agent/")), "")
        print(f"{issue.number:<4} {state[:13]:<14} {area[:15]:<16} {agent[:13]:<14} {issue.title[:60]}")


def cmd_status(args) -> None:
    workers = get_worker_status()
    print("\nWorker Status:")
    print(f"{'Worker':<26} {'Role':<14} {'Status':<8} {'Temp'}")
    print("-" * 70)
    for w in workers:
        temp = f"{w.temperature_c:.1f}°C" if w.temperature_c else "n/a"
        print(f"{w.id:<26} {w.role:<14} {w.status:<8} {temp}")


def cmd_dispatch(args) -> None:
    token = get_github_token()
    workers = get_worker_status()
    issues = list_open_issues(token)

    solver_ready = [i for i in issues if i.is_solver_ready and i.is_solver_marked and not i.is_human_only]

    print(f"\n=== AIS Dispatch ({len(solver_ready)} solver-ready Issues) ===")
    for issue in solver_ready:
        best = best_worker_for_issue(issue, workers)
        worker_name = best.id if best else "NONE (offline)"
        print(f"  #{issue.number:<4} [{worker_name:<22}] {issue.title[:55]}")


def cmd_solve(args) -> None:
    token = get_github_token()
    issues = list_open_issues(token)
    issue = next((i for i in issues if i.number == args.issue), None)
    if not issue:
        print(f"Issue #{args.issue} nicht gefunden.")
        sys.exit(1)

    model = args.model or ("anthropic/claude-sonnet-4" if issue.needs_node_red else "minimax/minimax-m3")
    print(f"\n→ Solving Issue #{issue.number} mit {model}")
    result = dispatch_solve(issue, token, model=model, dry_run=args.dry_run)
    print(json.dumps(result, indent=2))


def main() -> int:
    parser = argparse.ArgumentParser(description="AIS Orchestrator — Hermes als Steuerzentrale")
    sub = parser.add_subparsers()

    p_list = sub.add_parser("list", help="Liste offene Issues")
    p_list.set_defaults(cmd="list")

    p_status = sub.add_parser("status", help="Worker Status anzeigen")
    p_status.set_defaults(cmd="status")

    p_dispatch = sub.add_parser("dispatch", help="Zeigt welche Issues an wen gehen würden")
    p_dispatch.set_defaults(cmd="dispatch")

    p_solve = sub.add_parser("solve", help="Löst ein einzelnes Issue")
    p_solve.add_argument("--issue", type=int, required=True)
    p_solve.add_argument("--model", default=None)
    p_solve.add_argument("--dry-run", action="store_true")
    p_solve.set_defaults(cmd="solve")

    args = parser.parse_args()
    if not hasattr(args, "cmd"):
        parser.print_help()
        return 0

    if args.cmd == "list":
        cmd_list(args)
    elif args.cmd == "status":
        cmd_status(args)
    elif args.cmd == "dispatch":
        cmd_dispatch(args)
    elif args.cmd == "solve":
        cmd_solve(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
