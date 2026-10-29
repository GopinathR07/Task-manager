"""Q4: CSV -> validate -> transform -> JSON data pipeline with a quality gate."""
import csv
import json
import sys


def run_pipeline(src="input.csv", out="output.json", rejected_out="rejected.json"):
    valid, rejected = [], []

    with open(src, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for line_no, row in enumerate(reader, start=2):  # line 1 is the header
            try:
                record_id = int(row["id"])
                name = (row["name"] or "").strip()
                marks = int(row["marks"])
            except (ValueError, TypeError, KeyError) as e:
                rejected.append({"line": line_no, "row": row, "reason": f"bad value: {e}"})
                continue
            if not name:
                rejected.append({"line": line_no, "row": row, "reason": "name is blank"})
                continue
            if not 0 <= marks <= 100:
                rejected.append({"line": line_no, "row": row, "reason": "marks outside 0-100"})
                continue
            valid.append({
                "id": record_id,
                "name": name,
                "marks": marks,
                "result": "PASS" if marks >= 50 else "FAIL",
            })

    with open(out, "w", encoding="utf-8") as f:
        json.dump(valid, f, indent=2)
    with open(rejected_out, "w", encoding="utf-8") as f:
        json.dump(rejected, f, indent=2)

    print("Pipeline completed")
    print("Valid records:", len(valid))
    print("Rejected records:", len(rejected))
    for r in rejected:
        print(f"  line {r['line']}: {r['reason']}")
    return valid, rejected


if __name__ == "__main__":
    valid, _ = run_pipeline(*sys.argv[1:2])
    # Quality gate: fail the CI job if nothing valid was produced
    sys.exit(0 if valid else 1)
