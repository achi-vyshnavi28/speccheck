# SpecCheck evaluation: development set (rules were tuned on it)

100 labelled requirements (54 with at least one defect, 46 clean), 61 defects in total. Source: `evals/requirements.yaml`.

| System | Precision | Recall | F1 | Item accuracy (flag / don't flag) | False alarms on clean requirements |
|---|---|---|---|---|---|
| Rules only | 97% | 97% | 97% | 98% | 0% |
| LLM only | 83% | 98% | 90% | 95% | 11% |
| Rules + LLM (union) | 82% | 100% | 90% | 95% | 11% |

## Per defect type (rules only)

| Defect | Support | Found | Missed | False alarms |
|---|---|---|---|---|
| vague_term | 22 | 22 | 0 | 0 |
| placeholder | 3 | 3 | 0 | 0 |
| weak_modal | 9 | 9 | 0 | 0 |
| missing_value | 7 | 7 | 0 | 1 |
| ambiguous_reference | 4 | 4 | 0 | 0 |
| missing_actor | 7 | 5 | 2 | 1 |
| gxp_control_missing | 9 | 9 | 0 | 0 |

## Where the rules disagree with the labels

| Requirement | Missed | Extra |
|---|---|---|
| The system should warn the operator when a value is close to the limit. | - | missing_value |
| The investigation report can be modified after approval. | - | missing_actor |
| Every change request needs an impact assessment and approval before implementation. | missing_actor | - |
| Role changes are approved before they take effect. | missing_actor | - |
