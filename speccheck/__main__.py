"""SpecCheck CLI.

    python -m speccheck samples/PRD-1.1_cleaning_log_and_rejection.md --version 1.1
    python -m speccheck <prd.md> --version 1.1 --no-llm      # rules only (no API key needed)
"""

import argparse
import json
from pathlib import Path

from dotenv import load_dotenv

from speccheck.export import excel_library, jira_csv, playwright_skeletons, review_report
from speccheck.pipeline import run

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("prd", type=Path)
    p.add_argument("--version", required=True)
    p.add_argument("--no-llm", action="store_true")
    p.add_argument("--epic", default="", help="Jira label for the stories (default: PRD file name)")
    p.add_argument("--out", type=Path, default=None, help="default: outputs/<prd name>/")
    args = p.parse_args()
    load_dotenv(ROOT / ".env")

    r = run(args.prd.read_text(encoding="utf-8"), use_llm=not args.no_llm)
    for sid, why in r.skipped.items():
        print(f"{sid}: drafting skipped ({why})")
    out = args.out or ROOT / "outputs" / args.prd.stem
    out.mkdir(parents=True, exist_ok=True)
    current = out / f"test_library_v{args.version}.xlsx"
    previous = sorted(p for p in out.glob("test_library_v*.xlsx") if p != current)
    excel_library(current, args.version, r.title, r.stories, r.drafts, r.gaps, previous[-1] if previous else None)
    epic = args.epic or args.prd.stem.split("_")[0]
    files = {f"jira_import_v{args.version}.csv": jira_csv(r.stories, r.gaps, epic),
             f"spec_review_v{args.version}.md": review_report(r.title, r.stories, r.drafts, r.gaps),
             f"test_playwright_v{args.version.replace('.', '_')}.py": playwright_skeletons(r.title, r.stories, r.drafts)}
    if r.drafts:  # saved so the web app can show these drafts without an API key
        files["drafts.json"] = json.dumps({k: v.model_dump() for k, v in r.drafts.items()}, indent=1)
    for name, text in files.items():
        (out / name).write_text(text, encoding="utf-8")
    total = sum(len(d.test_cases) for d in r.drafts.values())
    print(f"{len(r.stories)} stories · {total} draft test cases · {len(r.gaps)} gaps ({len(r.blocking)} blocking)\n"
          f"{current}\n" + "\n".join(str(out / n) for n in files))


if __name__ == "__main__":
    main()
