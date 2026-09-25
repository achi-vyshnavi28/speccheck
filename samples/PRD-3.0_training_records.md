# PRD 3.0: Training records and qualification gates

**Author:** Product · **Status:** Draft for review · **Target release:** 3.0

## Problem
Operators sometimes execute a step on an SOP version they were never trained on. Auditors ask for training evidence
per batch, and it takes QA days to assemble it from the LMS and paper files.

## User stories

### TR-301 Assign training when an SOP changes
As a training coordinator, I want training assigned automatically when a new SOP version becomes effective.
- When an SOP version becomes effective, every user whose role requires that SOP receives a training assignment.
- The assignment is due 14 days after the effective date.
- Users who are on leave are handled appropriately.

### TR-302 Record training completion
As a trainee, I want to record that I completed training, so my qualification is up to date.
- The trainee confirms completion with an e-signature, stating the SOP number and version.
- The trainer verifies the completion with an e-signature; the trainer cannot be the trainee.
- A read-and-understood assignment needs no trainer verification.

### TR-303 Block untrained users
As QA, I want untrained users blocked from executing batch steps, so only qualified people perform GMP work.
- A user cannot sign a batch step unless they have a completed training record for the current version of the SOP linked to that step.
- The block message names the missing SOP and version.
- It must be possible to override this in an emergency.

### TR-304 Training evidence per batch
As a QA reviewer, I want a training report per batch, so I can answer auditors in minutes.
- The report lists every person who signed a step, the SOPs linked to their steps, and the training completion date for each.
- The report should be fast.
- The report can be exported.

### TR-305 Correct a training record
As a training coordinator, I want to correct a wrong completion date.
- The coordinator can change the completion date.
- The system keeps the old value.
