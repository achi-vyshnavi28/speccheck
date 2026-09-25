# PRD 4.0: Production logbook for equipment usage and cleaning (first draft)

**Author:** Product · **Status:** First draft, as received for review · **Target release:** 4.0

> Illustrative draft written for a SpecCheck work sample. It imitates the kind of first draft a product team
> circulates: mostly clear, with the gaps real drafts tend to have.

## Problem
Equipment usage and cleaning are recorded in paper logbooks. Entries are made at the end of the shift, cleaning
status is checked by asking around, and QA finds missing or illegible entries only at batch review.

## User stories

### LB-401 Record equipment usage
As an operator, I want to record when I start and finish using a piece of equipment, so the logbook shows who used it, for which batch.
- The operator scans the equipment tag and selects the product and batch.
- Start and end time are recorded.
- Recording should be quick on the shop floor.

### LB-402 Record cleaning
As an operator, I want to record the cleaning I performed, so QA can see the equipment was cleaned to procedure.
- The operator selects the cleaning type (minor or major) and the cleaning SOP.
- Cleaning is verified.
- The entry is signed.

### LB-403 Show equipment status
As a supervisor, I want to see the status of every piece of equipment, so I don't start a batch on dirty equipment.
- Each item shows one of: in use, dirty, clean, clean hold expired.
- Clean hold time is TBD per equipment.
- The system prevents use of equipment that isn't clean.

### LB-404 Correct a logbook entry
As a supervisor, I want to correct wrong entries.
- The supervisor can edit entries as needed.

### LB-405 Logbook review
As QA, I want to review logbooks, so issues are found before batch release.
- QA reviews logbooks periodically.
- The review report can be exported.
