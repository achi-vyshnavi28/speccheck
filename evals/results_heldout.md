# SpecCheck evaluation: held-out set (written after the rules were frozen)

60 labelled requirements (35 with at least one defect, 25 clean), 37 defects in total. Source: `evals/heldout.yaml`.

| System | Precision | Recall | F1 | Item accuracy (flag / don't flag) | False alarms on clean requirements |
|---|---|---|---|---|---|
| Rules only | 90% | 70% | 79% | 85% | 0% |
| LLM only | 75% | 97% | 85% | 97% | 4% |
| Rules + LLM (union) | 73% | 100% | 84% | 98% | 4% |

## Per defect type (rules only)

| Defect | Support | Found | Missed | False alarms |
|---|---|---|---|---|
| vague_term | 11 | 5 | 6 | 0 |
| placeholder | 2 | 2 | 0 | 0 |
| weak_modal | 5 | 5 | 0 | 0 |
| missing_value | 3 | 3 | 0 | 1 |
| ambiguous_reference | 2 | 2 | 0 | 0 |
| missing_actor | 6 | 3 | 3 | 1 |
| gxp_control_missing | 8 | 6 | 2 | 1 |

## Where the rules disagree with the labels

| Requirement | Missed | Extra |
|---|---|---|
| Expired materials should be blocked automatically. | - | missing_value |
| Material status is changed from quarantine to released. | missing_actor | - |
| Stock levels must be accurate. | vague_term | - |
| Calibration certificates are uploaded and approved. | missing_actor | - |
| Calibration intervals can be extended by the engineer. | gxp_control_missing | - |
| Preventive maintenance is scheduled at suitable intervals. | vague_term | - |
| The trend chart should highlight unusual results. | vague_term | - |
| Serial numbers can be decommissioned by the packaging operator. | gxp_control_missing | - |
| Aggregation data is sent to the national repository without delay. | vague_term | - |
| The line should reject packs with unreadable codes. | - | gxp_control_missing |
| Audit findings are closed within the agreed period. | - | missing_actor |
| Case narratives must be clear and complete. | vague_term | - |
| Essential documents are QC-checked. | missing_actor | - |
| Cleaning must be effective. | vague_term | - |
