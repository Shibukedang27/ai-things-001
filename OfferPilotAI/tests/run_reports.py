#!/usr/bin/env python3
"""Run the OfferPilot AI test suite and generate durable test reports."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import time
import xml.etree.ElementTree as ET


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = PROJECT_ROOT / "tests" / "reports"
JUNIT_REPORT = REPORT_DIR / "junit.xml"
MARKDOWN_REPORT = REPORT_DIR / "TEST_REPORT.md"
JSON_REPORT = REPORT_DIR / "latest-summary.json"


def main() -> int:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    started_at = time.strftime("%Y-%m-%d %H:%M:%S %Z")
    command = [
        sys.executable,
        "-m",
        "pytest",
        "tests",
        "--junitxml",
        str(JUNIT_REPORT),
        *sys.argv[1:],
    ]

    result = subprocess.run(command, cwd=PROJECT_ROOT)
    summary = parse_junit(JUNIT_REPORT) if JUNIT_REPORT.exists() else empty_summary()
    summary["started_at"] = started_at
    summary["command"] = " ".join(command)
    summary["exit_code"] = result.returncode
    summary["status"] = "passed" if result.returncode == 0 else "failed"

    JSON_REPORT.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    MARKDOWN_REPORT.write_text(render_markdown(summary), encoding="utf-8")
    print(f"\nTest reports written to {REPORT_DIR}")
    return result.returncode


def empty_summary() -> dict:
    return {
        "tests": 0,
        "failures": 0,
        "errors": 0,
        "skipped": 0,
        "time": 0.0,
        "testcases": [],
        "failures_detail": [],
    }


def parse_junit(path: Path) -> dict:
    root = ET.parse(path).getroot()
    suites = list(root) if root.tag == "testsuites" else [root]
    summary = empty_summary()

    for suite in suites:
        summary["tests"] += int(suite.attrib.get("tests", "0"))
        summary["failures"] += int(suite.attrib.get("failures", "0"))
        summary["errors"] += int(suite.attrib.get("errors", "0"))
        summary["skipped"] += int(suite.attrib.get("skipped", "0"))
        summary["time"] += float(suite.attrib.get("time", "0"))

    for testcase in root.iter("testcase"):
        outcome_node = next(
            (child for child in testcase if child.tag in {"failure", "error", "skipped"}),
            None,
        )
        outcome = outcome_node.tag if outcome_node is not None else "passed"
        case = {
            "classname": testcase.attrib.get("classname", ""),
            "name": testcase.attrib.get("name", ""),
            "time": float(testcase.attrib.get("time", "0")),
            "outcome": outcome,
        }
        summary["testcases"].append(case)
        if outcome in {"failure", "error"}:
            summary["failures_detail"].append(
                {
                    **case,
                    "message": outcome_node.attrib.get("message", "") if outcome_node is not None else "",
                }
            )

    summary["time"] = round(summary["time"], 3)
    summary["testcases"].sort(key=lambda item: item["time"], reverse=True)
    return summary


def render_markdown(summary: dict) -> str:
    status_label = "PASSED" if summary["status"] == "passed" else "FAILED"
    lines = [
        "# OfferPilot AI Test Report",
        "",
        f"Status: **{status_label}**",
        f"Generated: `{summary['started_at']}`",
        f"Command: `{summary['command']}`",
        "",
        "## Suite Summary",
        "",
        "| Tests | Failures | Errors | Skipped | Time (s) | Exit Code |",
        "| ---: | ---: | ---: | ---: | ---: | ---: |",
        (
            f"| {summary['tests']} | {summary['failures']} | {summary['errors']} | "
            f"{summary['skipped']} | {summary['time']:.3f} | {summary['exit_code']} |"
        ),
        "",
        "## Slowest Tests",
        "",
    ]

    slowest = summary["testcases"][:10]
    if slowest:
        lines.extend(["| Test | Outcome | Time (s) |", "| --- | --- | ---: |"])
        lines.extend(
            f"| `{case['classname']}::{case['name']}` | {case['outcome']} | {case['time']:.3f} |"
            for case in slowest
        )
    else:
        lines.append("No test cases were recorded.")

    lines.extend(["", "## Failures", ""])
    if summary["failures_detail"]:
        lines.extend(
            f"- `{case['classname']}::{case['name']}`: {case['message'] or case['outcome']}"
            for case in summary["failures_detail"]
        )
    else:
        lines.append("No failures or errors.")

    lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
