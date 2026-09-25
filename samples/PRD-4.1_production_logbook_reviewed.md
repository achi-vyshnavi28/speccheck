# PRD 4.1: Production logbook for equipment usage and cleaning (after spec review)

**Author:** Product · **Status:** Reviewed; open decisions listed at the end · **Target release:** 4.0

> Revision of PRD 4.0 after a SpecCheck run and a human review. Every change answers a specific gap; decisions that
> only product or QA can make are listed as open questions, with a proposed default, instead of being guessed.

## User stories

### LB-401 Record equipment usage
As an operator, I want to record when I start and finish using a piece of equipment, so the logbook shows who used it, for which batch.
- The operator scans the equipment tag and selects the product and batch; the start time is the server time of the scan.
- Only an operator trained on the equipment's SOP can start usage; others are refused with a message naming the missing training.
- Starting usage is refused if the equipment status is not "clean", with a message showing the current status.
- The end time is the server time when the operator ends usage; an end time before the start time is impossible because both come from the server.
- A usage entry takes no more than 3 taps after scanning the tag.

### LB-402 Record cleaning
As an operator, I want to record the cleaning I performed, so QA can see the equipment was cleaned to procedure.
- The operator selects the cleaning type (minor or major) and the cleaning SOP, and signs with an e-signature (meaning: "Performed").
- A supervisor verifies a major cleaning with an e-signature (meaning: "Verified"); the supervisor cannot be the operator who performed it.
- Until a major cleaning is verified, the equipment status stays "dirty".
- A cleaning entry without the SOP is refused with a message naming the missing field.

### LB-403 Show equipment status
As a supervisor, I want to see the status of every piece of equipment, so I don't start a batch on dirty equipment.
- Each item shows one of: in use, dirty, clean, clean hold expired.
- The clean hold time is configured per equipment by QA; the default is 72 hours from the end of the cleaning.
- When the hold time passes, the status changes to "clean hold expired" and starting usage is refused.

### LB-404 Correct a logbook entry
As a supervisor, I want to correct a wrong entry, so the logbook is accurate without losing the original record.
- Only a supervisor or QA can correct an entry; an operator's attempt is refused.
- A correction requires a reason of at least 10 characters and an e-signature (meaning: "Corrected").
- The original value stays visible next to the corrected one, and the audit trail records user, time, old value, new value and reason.
- An entry linked to a released batch cannot be corrected; the attempt is refused and QA is notified by email within 15 minutes.

### LB-405 Logbook review
As QA, I want to review logbooks, so issues are found before batch release.
- A logbook review is required for every batch before release; release is blocked until the review is signed by QA.
- The review lists every entry for the equipment used by the batch, with corrections highlighted.
- The review report can be exported as PDF, including the signature manifest.
- A QA reviewer cannot review a batch in which they recorded a logbook entry.

## Open decisions (proposed defaults, need product/QA sign-off)
| # | Question | Proposed default | Why it matters |
|---|---|---|---|
| 1 | Clean hold time per equipment type | 72 h from end of cleaning | Tests currently assume a value the spec never set |
| 2 | Can a correction be made after the batch is released? | No; raise a deviation instead | Released records must stay locked (Part 11 §11.10) |
| 3 | Does a minor cleaning need verification? | No, only major | Changes the two-person rule and the test count |
| 4 | Offline use on the shop floor | Out of scope for 4.0 | Affects contemporaneous recording (ALCOA+) |
