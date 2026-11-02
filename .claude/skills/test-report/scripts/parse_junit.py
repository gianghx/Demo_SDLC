#!/usr/bin/env python3
"""Summarize one or more JUnit XML files for the test-report skill.

Usage:
    python parse_junit.py results.xml [more.xml ...] [--id-pattern "TC-\\d+"] [--json]

Prints counts (passed, failed, error, skipped, total) and the list of failing
tests with their messages. With --id-pattern, the first regex match found in
each test's name or classname is reported as its ID (useful for TC-xxx tags).
"""
import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET


def iter_testcases(root):
    if root.tag == "testcase":
        yield root
        return
    yield from root.iter("testcase")


def classify(case):
    for tag, status in (("error", "error"), ("failure", "failed"), ("skipped", "skipped")):
        node = case.find(tag)
        if node is not None:
            message = (node.get("message") or (node.text or "")).strip()
            return status, " ".join(message.split())[:300]
    return "passed", ""


def summarize(paths, id_pattern):
    pattern = re.compile(id_pattern) if id_pattern else None
    counts = {"passed": 0, "failed": 0, "error": 0, "skipped": 0}
    problems, duration = [], 0.0
    for path in paths:
        root = ET.parse(path).getroot()
        for case in iter_testcases(root):
            status, message = classify(case)
            counts[status] += 1
            duration += float(case.get("time") or 0)
            if status in ("failed", "error"):
                name = case.get("name", "")
                classname = case.get("classname", "")
                test_id = None
                if pattern:
                    match = pattern.search(f"{name} {classname}")
                    test_id = match.group(0) if match else None
                problems.append(
                    {"id": test_id, "name": name, "class": classname,
                     "status": status, "message": message}
                )
    counts["total"] = sum(counts.values())
    return {"counts": counts, "duration_seconds": round(duration, 2), "problems": problems}


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("files", nargs="+")
    parser.add_argument("--id-pattern", default=None)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    # Console Windows mặc định cp1252 không in được tiếng Việt trong thông báo lỗi của test.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    try:
        result = summarize(args.files, args.id_pattern)
    except (ET.ParseError, OSError) as exc:
        print(f"Cannot read JUnit XML: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    c = result["counts"]
    executed = c["passed"] + c["failed"] + c["error"]
    print(f"Total: {c['total']}  Passed: {c['passed']}  Failed: {c['failed']}  "
          f"Error: {c['error']}  Skipped: {c['skipped']}")
    if executed:
        print(f"Pass rate (of executed): {c['passed'] / executed:.1%}")
    if c["total"]:
        print(f"Pass rate (of total): {c['passed'] / c['total']:.1%}")
    print(f"Duration: {result['duration_seconds']}s")
    if result["problems"]:
        print("\nFailing tests:")
        for p in result["problems"]:
            label = p["id"] or p["name"]
            print(f"- [{p['status']}] {label} ({p['class']}): {p['message']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
