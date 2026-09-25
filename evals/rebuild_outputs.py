"""Rebuild the sample outputs from the saved LLM drafts (no API calls), e.g. after an export change.

    python -m evals.rebuild_outputs
"""

import json
from pathlib import Path

from speccheck.export import excel_library, jira_csv, playwright_skeletons, review_report, traceability
from speccheck.generate import Drafted
from speccheck.lint import lint
from speccheck.parse import parse_prd

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    for saved in sorted((ROOT / "outputs").glob("*/drafts.json")):
        out, name = saved.parent, saved.parent.name
        title, stories = parse_prd(ROOT / "samples" / f"{name}.md")
        gaps = lint(stories)
        drafts = {k: Drafted.model_validate(v) for k, v in json.loads(saved.read_text(encoding="utf-8")).items()}
        excel_library(out / "test_library_v1.0.xlsx", "1.0", title, stories, drafts, gaps)
        (out / "jira_import_v1.0.csv").write_text(jira_csv(stories, gaps, name.split("_")[0]), encoding="utf-8")
        (out / "spec_review_v1.0.md").write_text(review_report(title, stories, drafts, gaps), encoding="utf-8")
        (out / "test_playwright_v1_0.py").write_text(playwright_skeletons(title, stories, drafts), encoding="utf-8")
        trace = traceability(stories, drafts, gaps)
        print(f"{name}: {len(gaps)} gaps · {len(trace)} criteria · {sum(t.coverage == 'NO' for t in trace)} untested · "
              f"{sum(t.coverage == 'assumed' for t in trace)} tested on an assumption")


if __name__ == "__main__":
    main()
