"""SpecCheck web app: paste a PRD, get the requirement gaps, draft test cases, traceability and exports.

    streamlit run app.py
"""

import io
import json
import os
from pathlib import Path

import pandas as pd
import streamlit as st

from speccheck.export import case_id, excel_library, jira_csv, playwright_skeletons, review_report, traceability
from speccheck.generate import Drafted
from speccheck.lint import check
from speccheck.pipeline import Review, run

ROOT = Path(__file__).resolve().parent
SAMPLES = {p.stem: p for p in sorted((ROOT / "samples").glob("*.md"))}

st.set_page_config(page_title="SpecCheck", page_icon="🧪", layout="wide")
try:  # Streamlit Cloud secrets → environment (the LLM client reads GEMINI_API_KEY from the environment)
    for k, v in st.secrets.items():
        os.environ.setdefault(k, str(v))
except Exception:
    pass
HAS_KEY = bool(os.getenv("GEMINI_API_KEY"))


def saved_drafts(name: str) -> dict[str, Drafted]:
    path = ROOT / "outputs" / name / "drafts.json"
    if not path.exists():
        return {}
    return {k: Drafted.model_validate(v) for k, v in json.loads(path.read_text(encoding="utf-8")).items()}


@st.cache_data(show_spinner=False, ttl=3600)
def draft_with_llm(text: str) -> dict:
    r = run(text, use_llm=True)
    return {"drafts": {k: v.model_dump() for k, v in r.drafts.items()}, "skipped": r.skipped}


st.title("SpecCheck")
st.caption("Finds the requirements a tester can't test, before development starts, and drafts test cases for the "
           "rest. Built for GxP software (21 CFR Part 11, ALCOA+).")

with st.sidebar:
    st.header("Input")
    choice = st.radio("PRD source", ["Sample PRD", "Paste your own"])
    if choice == "Sample PRD":
        name = st.selectbox("Sample", list(SAMPLES), format_func=lambda s: s.replace("_", " "))
        text = SAMPLES[name].read_text(encoding="utf-8")
    else:
        name = None
        text = st.text_area("PRD in Markdown", height=320,
                            placeholder="# PRD title\n\n### US-101 Story title\nAs a ..., I want ..., so ...\n"
                                        "- acceptance criterion\n- acceptance criterion")
    use_llm = st.toggle("Draft test cases with AI (Gemini)", value=False, disabled=not HAS_KEY,
                        help="Rules always run. AI drafting needs GEMINI_API_KEY; samples include saved drafts.")
    st.markdown("**Format:** stories as `### US-101 Title` (any `ABC-123` id), criteria as bullets.")
    st.divider()
    st.markdown("[Source on GitHub](https://github.com/achi-vyshnavi28/speccheck) · "
                "[How it was evaluated](https://github.com/achi-vyshnavi28/speccheck/tree/main/evals)")

if not text.strip():
    st.info("Pick a sample or paste a PRD to start.")
    st.stop()

r: Review = run(text, use_llm=False)
if not r.stories:
    st.warning("No user stories found. Use headings like `### US-101 Title` followed by bullet criteria.")
    st.stop()

source = ""
if use_llm:
    with st.spinner("Drafting test cases with Gemini (about 10 s per story)..."):
        out = draft_with_llm(text)
    r.drafts = {k: Drafted.model_validate(v) for k, v in out["drafts"].items()}
    r.skipped = out["skipped"]
elif name and (d := saved_drafts(name)):
    r.drafts, source = d, "saved"

(st.error if r.blocking else st.success)(
    f"**{'NOT ready for development' if r.blocking else 'Ready for development'}**: {len(r.blocking)} blocking "
    f"gap(s), {len(r.gaps) - len(r.blocking)} other, across {len(r.stories)} stories.")
trace = traceability(r.stories, r.drafts, r.gaps)
c1, c2, c3, c4 = st.columns(4)
c1.metric("Stories", len(r.stories))
c2.metric("Acceptance criteria", sum(len(s.criteria) for s in r.stories))
c3.metric("Requirement gaps", len(r.gaps))
c4.metric("Draft test cases", sum(len(d.test_cases) for d in r.drafts.values()) if r.drafts else "-")
if source == "saved":
    st.caption("Test cases for this sample were drafted earlier with Gemini and saved. They stay 'draft' until a "
               "person reviews them.")
for sid, why in r.skipped.items():
    st.warning(f"{sid}: AI drafting skipped ({why}). The rule review is complete.")

tab_gaps, tab_cases, tab_trace, tab_export, tab_try = st.tabs(
    ["Requirement gaps", "Draft test cases", "Traceability", "Export", "Check one requirement"])

with tab_gaps:
    order = {"high": 0, "medium": 1, "low": 2}
    sev = st.multiselect("Severity", list(order), default=list(order))
    rows = [{"Story": g.story, "Severity": g.severity, "Rule": g.rule.replace("_", " "), "Requirement": g.text,
             "Why it can't be tested": g.why, "Question for product": g.question}
            for g in sorted(r.gaps, key=lambda g: order[g.severity]) if g.severity in sev]
    st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)
    st.caption("Rules run without AI, so the same PRD always gives the same gaps.")

with tab_cases:
    if not r.drafts:
        st.info("Turn on AI drafting in the sidebar, or pick a sample to see saved drafts.")
    for s in r.stories:
        d = r.drafts.get(s.id, Drafted(test_cases=[]))
        with st.expander(f"{s.id} {s.title}: {len(d.test_cases)} case(s)"):
            st.markdown("\n".join(f"{i}. {c}" for i, c in enumerate(s.criteria, start=1)))
            if d.test_cases:
                st.dataframe(pd.DataFrame([{"ID": case_id(s, n), "Covers AC": ", ".join(map(str, tc.covers)),
                                            "Type": tc.type, "Title": tc.title, "Steps": " → ".join(tc.steps),
                                            "Expected": tc.expected, "Priority": tc.priority}
                                           for n, tc in enumerate(d.test_cases, start=1)]),
                             hide_index=True, use_container_width=True)
            for a in d.ambiguities:
                st.warning(f"Could not write an exact expected result: {a}")

with tab_trace:
    st.dataframe(pd.DataFrame([{"Story": t.story, "AC": t.number, "Acceptance criterion": t.criterion,
                                "Test cases": ", ".join(t.cases) or "-", "Open gaps": ", ".join(t.gaps) or "-",
                                "Covered": "yes" if t.cases else "NO"} for t in trace]),
                 hide_index=True, use_container_width=True)
    if r.drafts:
        st.caption(f"{sum(not t.cases for t in trace)} of {len(trace)} criteria have no test case.")

with tab_export:
    version = st.text_input("Version", "1.0")
    buf = io.BytesIO()
    excel_library(buf, version, r.title, r.stories, r.drafts, r.gaps)
    epic = (name or "prd").split("_")[0]
    st.download_button("Excel test library (test cases, traceability, gaps, change log)", buf.getvalue(),
                       f"test_library_v{version}.xlsx")
    st.download_button("Jira CSV import (stories + gap tasks)", jira_csv(r.stories, r.gaps, epic),
                       f"jira_import_v{version}.csv", "text/csv")
    st.download_button("Spec review (Markdown)", review_report(r.title, r.stories, r.drafts, r.gaps),
                       f"spec_review_v{version}.md", "text/markdown")
    st.download_button("Playwright test skeletons (Python)", playwright_skeletons(r.title, r.stories, r.drafts),
                       f"test_playwright_v{version.replace('.', '_')}.py", "text/x-python", disabled=not r.drafts)

with tab_try:
    one = st.text_input("Requirement", "QA can override the cleaning check as needed.")
    findings = check(one)
    if not findings:
        st.success("No defects found by the rules.")
    for f in findings:
        st.markdown(f"- **{f.rule.replace('_', ' ')}** ({f.severity}): {f.why} → *{f.question}*")
