"""Measure SpecCheck against the labelled requirements in evals/requirements.yaml.

    python -m evals.run_eval            # rules + LLM (needs GEMINI_API_KEY)
    python -m evals.run_eval --no-llm   # rules only

Writes evals/results.md and evals/results.json. LLM labels are cached in evals/llm_labels.json so the
numbers can be re-scored without new API calls (delete the file to re-query).
"""

import argparse
import json
from pathlib import Path

import yaml
from dotenv import load_dotenv

from speccheck.generate import DEFECTS, review
from speccheck.lint import check

HERE = Path(__file__).resolve().parent


def score(gold: list[set], pred: list[set]) -> dict:
    per = {}
    for t in DEFECTS:
        tp = sum(t in g and t in p for g, p in zip(gold, pred))
        fp = sum(t not in g and t in p for g, p in zip(gold, pred))
        fn = sum(t in g and t not in p for g, p in zip(gold, pred))
        per[t] = {"tp": tp, "fp": fp, "fn": fn, "support": tp + fn}
    tp, fp, fn = (sum(v[k] for v in per.values()) for k in ("tp", "fp", "fn"))
    flagged_ok = sum(bool(g) == bool(p) for g, p in zip(gold, pred))
    clean = [p for g, p in zip(gold, pred) if not g]
    return {"per_type": per, "precision": tp / (tp + fp) if tp + fp else 0.0, "recall": tp / (tp + fn) if tp + fn else 0.0,
            "item_accuracy": flagged_ok / len(gold), "false_alarm_rate": sum(bool(p) for p in clean) / len(clean)}


def f1(p: float, r: float) -> float:
    return 2 * p * r / (p + r) if p + r else 0.0


def pct(x: float) -> str:
    return f"{100 * x:.0f}%"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-llm", action="store_true")
    args = ap.parse_args()
    load_dotenv(HERE.parent / ".env")

    items = yaml.safe_load((HERE / "requirements.yaml").read_text(encoding="utf-8"))["items"]
    texts = [i["text"] for i in items]
    gold = [set(i["gold"]) for i in items]
    systems = {"Rules only": [{f.rule for f in check(t)} for t in texts]}
    if not args.no_llm:
        cache = HERE / "llm_labels.json"
        if cache.exists() and json.loads(cache.read_text())["texts"] == texts:
            llm = json.loads(cache.read_text())["labels"]
        else:
            llm = review(texts)
            cache.write_text(json.dumps({"texts": texts, "labels": llm}, indent=1))
        systems["LLM only"] = [set(x) for x in llm]
        systems["Rules + LLM (union)"] = [r | set(x) for r, x in zip(systems["Rules only"], llm)]

    results = {name: score(gold, pred) for name, pred in systems.items()}
    n_def = sum(bool(g) for g in gold)
    lines = ["# SpecCheck evaluation", "",
             f"{len(items)} labelled requirements ({n_def} with at least one defect, {len(items) - n_def} clean), "
             f"{sum(len(g) for g in gold)} defects in total. Source: `evals/requirements.yaml`.", "",
             "| System | Precision | Recall | F1 | Item accuracy (flag / don't flag) | False alarms on clean requirements |",
             "|---|---|---|---|---|---|"]
    for name, r in results.items():
        lines.append(f"| {name} | {pct(r['precision'])} | {pct(r['recall'])} | {pct(f1(r['precision'], r['recall']))} | "
                     f"{pct(r['item_accuracy'])} | {pct(r['false_alarm_rate'])} |")
    lines += ["", "## Per defect type (rules only)", "", "| Defect | Support | Found | Missed | False alarms |", "|---|---|---|---|---|"]
    for t, v in results["Rules only"]["per_type"].items():
        lines.append(f"| {t} | {v['support']} | {v['tp']} | {v['fn']} | {v['fp']} |")
    misses = [(t, sorted(g - p), sorted(p - g)) for t, g, p in zip(texts, gold, systems["Rules only"]) if g != p]
    lines += ["", "## Where the rules disagree with the labels", "", "| Requirement | Missed | Extra |", "|---|---|---|"]
    lines += [f"| {t} | {', '.join(m) or '-'} | {', '.join(e) or '-'} |" for t, m, e in misses]
    (HERE / "results.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (HERE / "results.json").write_text(json.dumps(results, indent=1), encoding="utf-8")
    print("\n".join(lines[:8 + len(results)]))


if __name__ == "__main__":
    main()
