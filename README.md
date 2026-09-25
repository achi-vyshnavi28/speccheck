# SpecCheck: catch untestable requirements before development starts

In regulated software (pharma, 21 CFR Part 11), a requirement nobody can test becomes a validation problem later:
a vague acceptance criterion turns into a test case with no exact expected result, then into a deviation. SpecCheck
reviews a PRD **before** development, the way a validation or QA reviewer would:

1. **Finds requirement defects** with deterministic rules: vague terms, placeholders, weak "should/may", limits with
   no value, missing actor (ALCOA+ *Attributable*), and GMP-relevant changes without a reason, e-signature or
   audit-trail entry (Part 11 §11.10(e), §11.50). Each one comes with the question to send back to product.
2. **Drafts test cases** with an LLM (Gemini): positive, negative, boundary, permission and audit cases, each linked to
   the acceptance criteria it covers. When a criterion is too vague for an exact expected result, the model logs an
   ambiguity instead of inventing one.
3. **Builds the traceability matrix** (criterion → test cases) and flags every criterion without a test.
4. **Exports** a versioned Excel test library (with change log), a Jira CSV import (stories + one task per gap),
   a spec-review report, and Playwright test skeletons for automation.

**Try it:** web app (`streamlit run app.py`), or the CLI:
```bash
python -m speccheck samples/PRD-2.0_capa_management.md --version 1.0            # rules + LLM drafting
python -m speccheck samples/PRD-2.0_capa_management.md --version 1.0 --no-llm   # rules only, no API key
```

## How well does it work? (measured, not claimed)
Two labelled sets of requirements in the style of pharma QMS/MES/LIMS specifications, labelled with the defects a
careful reviewer would raise, including ones no rule can catch.

| Set | Items | Purpose |
|---|---|---|
| `evals/requirements.yaml` | 100 (54 defective) | development: the rules were tuned on it |
| `evals/heldout.yaml` | 60 (35 defective) | **held-out: written after the rules were frozen**, from different areas (warehouse, calibration, environmental monitoring, complaints, serialization, suppliers, pharmacovigilance, eTMF) |

The git history shows the order: rules frozen in `291cab9`, held-out set added in `ef4bb46`. After that, two false
alarms found on the sample PRDs were fixed ("due date" read as a missing limit; "cannot be closed" read as a missing
actor). Re-scoring the held-out set before and after the fix gives the same result, so the numbers below are still blind.

**Held-out results** (`python -m evals.run_eval --set heldout`)

| System | Precision | Recall | F1 | False alarms on clean requirements |
|---|---|---|---|---|
| Rules only | **90%** | 70% | 79% | **0%** |
| LLM only (Gemini flash-lite) | 75% | 97% | 85% | 4% |
| Rules + LLM | 73% | **100%** | 84% | 4% |

On the development set, rules score 97% / 97%. That gap against the held-out set is the honest measure of
overfitting, and the reason both numbers are published.

**What this means for the design.** Rules are precise, repeatable and auditable, but only know the words they were
given (they missed "accurate", "effective", "without delay"). The LLM catches almost everything but adds false alarms.
So SpecCheck uses rules as the gate (same PRD → same result, which matters in a validated process) and the LLM as a
second reviewer whose output is always marked *draft* for a person to confirm.

**Cross-check from the samples.** On the three sample PRDs, the only acceptance criteria the LLM would not write a
test case for were exactly the ones the rules flagged as vague ("quickly and user-friendly", "handled
appropriately", "should be fast", "TBD"). Two independent methods agreeing on the same untestable lines.

## Questions answered with SQL
The labels and every system's predictions are loaded into SQLite (`python -m evals.to_sqlite` → `evals/eval.sqlite`)
and questioned in [`evals/questions.sql`](evals/questions.sql) (CTEs, window functions, anti-joins). Answers are in
[`evals/sql_answers.md`](evals/sql_answers.md); the totals match the Python evaluation exactly, which cross-checks both.

| Question | Answer |
|---|---|
| Where do the rules miss most? (Q2) | Calibration and maintenance (75% of defects missed) and serialization (67%): domain phrasing like "suitable intervals" and "without delay" is not in the vocabulary. That's where to extend it next |
| What did only the LLM catch? (Q3) | 11 defects, mostly vague terms ("accurate", "effective") and passive actions with no role ("QC-checked") |
| What does each reviewer cost? (Q4) | On clean requirements the rules raised 0 false alarms in 71; the LLM raised 6 |
| How much did the rules overfit? (Q5) | Vague-term recall fell from 100% (development) to 45% (held-out); placeholder, weak modal, missing value and pronoun rules held at 100% |

## Samples and outputs
| PRD | Stories | Gaps (blocking) | Draft test cases | Outputs |
|---|---|---|---|---|
| `PRD-1.1_cleaning_log_and_rejection` (from [BatchGuard](https://github.com/achi-vyshnavi28/batchguard)) | 5 | 9 (3) | 23 | `outputs/PRD-1.1_…/` |
| `PRD-2.0_capa_management` | 6 | 9 (2) | 27 | `outputs/PRD-2.0_…/` |
| `PRD-3.0_training_records` | 5 | 8 (1) | 23 | `outputs/PRD-3.0_…/` |

## Project layout
```
speccheck/parse.py      Markdown PRD → stories and acceptance criteria (any ABC-123 story id)
speccheck/lint.py       the rules: check() for one requirement, lint() adds story-level rules
speccheck/generate.py   Gemini REST client, test-case drafting, LLM defect review
speccheck/export.py     Excel library, traceability, Jira CSV, review report, Playwright skeletons
speccheck/pipeline.py   one review run, shared by the CLI and the web app
app.py                  Streamlit web app
evals/                  labelled sets, runner, results (results_heldout.md, results_dev.md)
tests/                  22 pytest tests (rules, false-alarm guards, exports, LLM failure handling)
```

## Limitations
- Both evaluation sets were written and labelled by the author. A second, independent labeller is the next step.
- 160 requirements is small; per-rule numbers on the held-out set rest on 2–11 examples each.
- LLM drafts are a starting point: they must be reviewed before they enter a validated test library.
- The rules are English-only and keyword-based; synonyms outside the lists are missed (see recall above).

## Run it
```bash
py -3.12 -m venv .venv && .venv\Scripts\activate
pip install -r requirements.txt
pytest -q
streamlit run app.py
```
Set `GEMINI_API_KEY` in `.env` (or Streamlit secrets) to enable LLM drafting; everything else works without it.
