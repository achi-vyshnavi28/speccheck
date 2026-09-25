"""Low-fidelity wireframes as SVG (pasted into Figma as editable layers).

    python design/make_wireframes.py

02 shows the traceability view as built; 01 and 03 are design proposals drawn before building.
"""

from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).parent / "wireframes"
W, H = 1280, 800
INK, MUTED, LINE, FILL, ACCENT, BAD, OK = "#1c2330", "#6b7280", "#d0d5dd", "#f2f4f7", "#ff4b4b", "#b42318", "#1a7f4b"


class Frame:
    def __init__(self, title: str, tab: int):
        self.title = title
        self.parts = [f'<rect width="{W}" height="{H}" fill="#ffffff"/>', f'<rect width="280" height="{H}" fill="#f0f2f6"/>']
        self.text(24, 50, "Input", 18, weight=700)
        self.text(24, 84, "PRD source", 13, MUTED)
        self.text(24, 108, "● Sample PRD   ○ Paste your own", 13)
        self.box(24, 124, 230, 36, "#fff")
        self.text(36, 147, "PRD-2.0 capa management", 13)
        self.text(310, 60, "SpecCheck", 32, weight=700)
        self.text(310, 86, "Finds the requirements a tester can't test, before development starts.", 13, MUTED)
        tabs = ["Requirement gaps", "Draft test cases", "Traceability", "Export", "Evaluation"]
        x = 310
        for i, t in enumerate(tabs):
            self.text(x, 130, t, 13, ACCENT if i == tab else INK)
            if i == tab:
                self.parts.append(f'<rect x="{x}" y="138" width="{7 * len(t)}" height="3" fill="{ACCENT}"/>')
            x += 7 * len(t) + 28
        self.parts.append(f'<line x1="310" y1="141" x2="1250" y2="141" stroke="{LINE}"/>')

    def text(self, x, y, s, size=14, color=INK, weight=400, anchor="start"):
        self.parts.append(f'<text x="{x}" y="{y}" fill="{color}" font-size="{size}" font-weight="{weight}" '
                          f'text-anchor="{anchor}" font-family="Inter, Arial">{escape(s)}</text>')

    def box(self, x, y, w, h, fill=FILL, stroke=LINE, r=8):
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}"/>')

    def button(self, x, y, label, primary=True, w=None, color=ACCENT):
        w = w or 20 + 8 * len(label)
        self.box(x, y, w, 30, color if primary else "#fff", color if primary else LINE, 6)
        self.text(x + w / 2, y + 20, label, 12, "#fff" if primary else INK, 600, "middle")

    def table(self, x, y, cols, rows, widths, colors=None, fills=None):
        self.box(x, y, sum(widths), 36 + 34 * len(rows), "#fff")
        cx = x
        for c, w in zip(cols, widths):
            self.text(cx + 10, y + 23, c, 12, MUTED, 600)
            cx += w
        for i, row in enumerate(rows):
            ry = y + 36 + 34 * i
            if fills and i in fills:
                self.parts.append(f'<rect x="{x + 1}" y="{ry}" width="{sum(widths) - 2}" height="34" fill="{fills[i]}"/>')
            self.parts.append(f'<line x1="{x}" y1="{ry}" x2="{x + sum(widths)}" y2="{ry}" stroke="{LINE}"/>')
            cx = x
            for j, (cell, w) in enumerate(zip(row, widths)):
                self.text(cx + 10, ry + 22, cell, 12, (colors or {}).get((i, j), INK))
                cx += w

    def note(self, x, y, lines):
        self.box(x, y, 320, 26 + 20 * len(lines), "#fffbe6", "#f5c542", 6)
        for i, line in enumerate(lines):
            self.text(x + 12, y + 22 + 20 * i, line, 12, "#7a5c00")

    def bar(self, x, y, label, pct, color):
        self.text(x, y + 14, label, 12)
        self.box(x + 250, y, 300, 20, FILL, FILL, 3)
        self.box(x + 250, y, 3 * pct, 20, color, color, 3)
        self.text(x + 560, y + 15, f"{pct}%", 12, MUTED)

    def svg(self):
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">'
                f"<title>{escape(self.title)}</title>" + "".join(self.parts) + "</svg>")


def triage():
    f = Frame("01 Gap triage workflow (proposal)", 0)
    f.box(310, 160, 940, 40, "#fce4e4", BAD, 6)
    f.text(326, 186, "NOT ready for development: 9 gaps (2 blocking) · 2 accepted · 1 rejected · 6 awaiting product", 14, BAD, 600)
    rows = [["CAPA-205", "high", "gxp control missing", "The owner can edit any field of a closed CAPA.", "Accepted", "Meera (PM)"],
            ["CAPA-206", "high", "placeholder", "TBD: what happens if the CAPA was not effective.", "Open", "–"],
            ["CAPA-202", "medium", "vague term", "Due dates must be reasonable.", "Accepted", "Meera (PM)"],
            ["CAPA-203", "medium", "vague term", "Escalations happen quickly.", "Open", "–"],
            ["CAPA-202", "low", "weak modal", "The assignee should receive a notification.", "Rejected", "Optional by design"]]
    f.table(310, 215, ["Story", "Sev.", "Rule", "Requirement", "Decision", "Owner / reason"], rows,
            [85, 65, 140, 390, 90, 170], colors={(0, 1): BAD, (1, 1): BAD, (0, 4): OK, (2, 4): OK, (4, 4): MUTED})
    f.text(310, 440, "Selected: CAPA-203 \"Escalations happen quickly.\"", 14, weight=600)
    f.box(310, 452, 620, 60, "#fff")
    f.text(322, 476, "Reason (required to reject; kept in the review history)", 12, MUTED)
    f.button(310, 525, "Accept → create Jira task", w=190, color=OK)
    f.button(510, 525, "Reject with reason", primary=False, w=150)
    f.button(670, 525, "Assign to product", primary=False, w=150)
    f.note(930, 560, ["Why: every decision becomes a new, independent", "label (the README's biggest limitation).",
                      "Rejected gaps feed the next rule review;", "accepted ones go straight to Jira."])
    return f


def trace():
    f = Frame("02 Traceability view (built)", 2)
    rows = [["CAPA-201", "1", "The CAPA copies the deviation number, product and root cause…", "TC-201-01", "-", "yes"],
            ["CAPA-202", "2", "Due dates must be reasonable.", "TC-202-03, TC-202-05", "vague term", "assumed"],
            ["CAPA-203", "2", "Escalations happen quickly.", "TC-203-01, TC-203-03", "vague term", "assumed"],
            ["CAPA-204", "1", "A CAPA cannot be closed while any action is open.", "TC-204-01, TC-204-02", "-", "yes"],
            ["CAPA-205", "1", "The owner can edit any field of a closed CAPA.", "TC-205-01 … 04", "gxp control missing", "assumed"],
            ["CAPA-206", "3", "TBD: what happens if the CAPA was not effective.", "-", "placeholder", "NO"]]
    amber = "#fff4e0"
    f.table(310, 165, ["Story", "AC", "Acceptance criterion", "Test cases", "Open gaps", "Covered"], rows,
            [90, 40, 410, 160, 170, 70], colors={(5, 5): BAD},
            fills={1: amber, 2: amber, 4: amber, 5: "#fce4e4"})
    f.text(310, 420, "1 of 15 criteria has no test case (the TBD). 5 more are 'assumed': tested, but their tests rest on", 13, MUTED)
    f.text(310, 440, "assumptions until product answers the open gap: coverage alone would call them done.", 13, MUTED)
    f.note(930, 470, ["Red: no test. Amber: tested, but the", "expected result was assumed because the",
                      "criterion is vague. That's the risk a", "plain coverage % hides."])
    return f


def evaluation():
    f = Frame("03 Evaluation dashboard (proposal)", 4)
    f.text(310, 180, "Held-out set: 60 requirements written after the rules were frozen", 15, weight=600)
    for i, (label, value) in enumerate([("Rules precision", "90%"), ("Rules recall", "70%"), ("Rules + LLM recall", "100%"),
                                        ("False alarms (rules)", "0%")]):
        f.box(310 + 235 * i, 195, 220, 80, "#fff")
        f.text(326 + 235 * i, 222, label, 12, MUTED)
        f.text(326 + 235 * i, 258, value, 28, weight=700)
    f.text(310, 310, "Where the rules miss most (share of labelled defects missed, by area)", 14, weight=600)
    for i, (area, pct) in enumerate([("Calibration and maintenance", 75), ("Serialization", 67), ("Pharmacovigilance", 40),
                                     ("Warehouse and materials", 40), ("Environmental monitoring", 20),
                                     ("Complaints and recalls", 0)]):
        f.bar(310, 325 + 32 * i, area, pct, BAD if pct >= 50 else "#f5a623" if pct > 0 else OK)
    f.text(310, 540, "Source: evals/questions.sql (Q2) over evals/eval.sqlite", 12, MUTED)
    f.note(930, 330, ["Turns the SQL answers into a page PMs", "can read: where to extend the rule",
                      "vocabulary next, and what each", "reviewer (rules vs LLM) costs."])
    return f


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for f in (triage(), trace(), evaluation()):
        name = f.title.split(" (")[0].replace(" ", "_").lower()
        (OUT / f"{name}.svg").write_text(f.svg(), encoding="utf-8")
        print(OUT / f"{name}.svg")


if __name__ == "__main__":
    main()
