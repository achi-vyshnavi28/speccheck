"""Load both evaluation sets, the labels and every system's predictions into SQLite, so results can be questioned
with SQL (evals/questions.sql).

    python -m evals.to_sqlite        # writes evals/eval.sqlite
"""

import json
import re
import sqlite3
from pathlib import Path

import yaml

from speccheck.lint import check

HERE = Path(__file__).resolve().parent
DB = HERE / "eval.sqlite"
SETS = {"dev": "requirements.yaml", "heldout": "heldout.yaml"}

SCHEMA = """
CREATE TABLE requirement (id INTEGER PRIMARY KEY, eval_set TEXT NOT NULL, area TEXT NOT NULL, text TEXT NOT NULL);
CREATE TABLE gold (requirement_id INTEGER REFERENCES requirement(id), defect TEXT NOT NULL);
CREATE TABLE prediction (requirement_id INTEGER REFERENCES requirement(id), system TEXT NOT NULL, defect TEXT NOT NULL);
"""


def areas(path: Path) -> list[str]:
    """The '# --- area ---' comment above each item, in item order."""
    out, current = [], "general"
    for line in path.read_text(encoding="utf-8").splitlines():
        if m := re.match(r"\s*# --- (.+?) ---", line):
            current = m.group(1)
        elif line.strip().startswith("- text:"):
            out.append(current)
    return out


def main() -> None:
    DB.unlink(missing_ok=True)
    con = sqlite3.connect(DB)
    con.executescript(SCHEMA)
    for name, file in SETS.items():
        items = yaml.safe_load((HERE / file).read_text(encoding="utf-8"))["items"]
        llm_file = HERE / f"llm_labels_{name}.json"
        llm = json.loads(llm_file.read_text())["labels"] if llm_file.exists() else [None] * len(items)
        for item, area, llm_labels in zip(items, areas(HERE / file), llm):
            rid = con.execute("INSERT INTO requirement (eval_set, area, text) VALUES (?, ?, ?)",
                              (name, area, item["text"])).lastrowid
            con.executemany("INSERT INTO gold VALUES (?, ?)", [(rid, d) for d in item["gold"]])
            rules = {f.rule for f in check(item["text"])}
            con.executemany("INSERT INTO prediction VALUES (?, 'rules', ?)", [(rid, d) for d in sorted(rules)])
            if llm_labels is not None:
                con.executemany("INSERT INTO prediction VALUES (?, 'llm', ?)", [(rid, d) for d in llm_labels])
    con.commit()
    n = con.execute("SELECT COUNT(*) FROM requirement").fetchone()[0]
    print(f"{DB.name}: {n} requirements, {con.execute('SELECT COUNT(*) FROM gold').fetchone()[0]} labelled defects, "
          f"{con.execute('SELECT COUNT(*) FROM prediction').fetchone()[0]} predictions")


if __name__ == "__main__":
    main()
