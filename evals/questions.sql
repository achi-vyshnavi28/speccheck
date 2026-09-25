-- Product questions about SpecCheck's accuracy, answered with SQL over evals/eval.sqlite.
-- Build the database: python -m evals.to_sqlite · Run: python -m evals.run_sql (writes evals/sql_answers.md)

-- Q1. On unseen requirements, how precise and complete is each system, per defect type?
WITH scored AS (
  SELECT s.system, d.defect,
         SUM(CASE WHEN g.defect IS NOT NULL AND p.defect IS NOT NULL THEN 1 ELSE 0 END) AS tp,
         SUM(CASE WHEN g.defect IS NULL     AND p.defect IS NOT NULL THEN 1 ELSE 0 END) AS fp,
         SUM(CASE WHEN g.defect IS NOT NULL AND p.defect IS NULL     THEN 1 ELSE 0 END) AS fn
  FROM requirement r
  CROSS JOIN (SELECT DISTINCT system FROM prediction) s
  CROSS JOIN (SELECT DISTINCT defect FROM gold) d
  LEFT JOIN gold g       ON g.requirement_id = r.id AND g.defect = d.defect
  LEFT JOIN prediction p ON p.requirement_id = r.id AND p.defect = d.defect AND p.system = s.system
  WHERE r.eval_set = 'heldout'
  GROUP BY s.system, d.defect
)
SELECT system, defect, tp + fn AS support, tp, fp, fn,
       ROUND(100.0 * tp / NULLIF(tp + fp, 0), 0) AS precision_pct,
       ROUND(100.0 * tp / NULLIF(tp + fn, 0), 0) AS recall_pct
FROM scored
ORDER BY system, support DESC;

-- Q2. Which requirement areas do the rules miss most on the held-out set? (where to add vocabulary next)
WITH per_area AS (
  SELECT r.area,
         COUNT(*) AS labelled_defects,
         SUM(CASE WHEN p.defect IS NULL THEN 1 ELSE 0 END) AS missed_by_rules
  FROM gold g
  JOIN requirement r ON r.id = g.requirement_id AND r.eval_set = 'heldout'
  LEFT JOIN prediction p ON p.requirement_id = g.requirement_id AND p.defect = g.defect AND p.system = 'rules'
  GROUP BY r.area
)
SELECT area, labelled_defects, missed_by_rules,
       ROUND(100.0 * missed_by_rules / labelled_defects, 0) AS miss_rate_pct,
       RANK() OVER (ORDER BY 1.0 * missed_by_rules / labelled_defects DESC) AS miss_rank
FROM per_area
ORDER BY miss_rank, area;

-- Q3. Which defects did only the LLM catch? (the case for keeping it as a second reviewer)
SELECT r.area, g.defect, r.text
FROM gold g
JOIN requirement r ON r.id = g.requirement_id AND r.eval_set = 'heldout'
WHERE EXISTS     (SELECT 1 FROM prediction p WHERE p.requirement_id = g.requirement_id AND p.defect = g.defect AND p.system = 'llm')
  AND NOT EXISTS (SELECT 1 FROM prediction p WHERE p.requirement_id = g.requirement_id AND p.defect = g.defect AND p.system = 'rules')
ORDER BY g.defect, r.area;

-- Q4. False alarms on clean requirements, per system and set (the cost of each reviewer)
SELECT r.eval_set, s.system,
       COUNT(*) AS clean_requirements,
       SUM(CASE WHEN EXISTS (SELECT 1 FROM prediction p WHERE p.requirement_id = r.id AND p.system = s.system)
                THEN 1 ELSE 0 END) AS flagged_anyway
FROM requirement r
CROSS JOIN (SELECT DISTINCT system FROM prediction) s
WHERE NOT EXISTS (SELECT 1 FROM gold g WHERE g.requirement_id = r.id)
GROUP BY r.eval_set, s.system
ORDER BY r.eval_set, s.system;

-- Q5. Overfitting check: rules' recall on the development set vs the held-out set, per defect type
SELECT g.defect,
       ROUND(100.0 * SUM(CASE WHEN r.eval_set = 'dev' AND p.defect IS NOT NULL THEN 1 ELSE 0 END)
             / NULLIF(SUM(CASE WHEN r.eval_set = 'dev' THEN 1 ELSE 0 END), 0), 0) AS dev_recall_pct,
       ROUND(100.0 * SUM(CASE WHEN r.eval_set = 'heldout' AND p.defect IS NOT NULL THEN 1 ELSE 0 END)
             / NULLIF(SUM(CASE WHEN r.eval_set = 'heldout' THEN 1 ELSE 0 END), 0), 0) AS heldout_recall_pct
FROM gold g
JOIN requirement r ON r.id = g.requirement_id
LEFT JOIN prediction p ON p.requirement_id = g.requirement_id AND p.defect = g.defect AND p.system = 'rules'
GROUP BY g.defect
ORDER BY heldout_recall_pct, g.defect;
