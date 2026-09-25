# PRD 2.0: CAPA management

**Author:** Product · **Status:** Draft for review · **Target release:** QMS 2.0

## Problem
Corrective and preventive actions (CAPAs) are tracked in a spreadsheet. Due dates slip without anyone noticing,
effectiveness checks are forgotten, and auditors find CAPAs closed without evidence.

## User stories

### CAPA-201 Create a CAPA from a deviation
As a QA specialist, I want to create a CAPA directly from a deviation, so the link between problem and action is never lost.
- The CAPA copies the deviation number, product and root cause category from the deviation.
- A CAPA cannot be created from a deviation that is still under investigation.
- Creating a CAPA is recorded in the audit trail with user, date and time.

### CAPA-202 Assign actions with due dates
As a CAPA owner, I want to assign actions to people with due dates, so everyone knows what they must do and by when.
- Each action has exactly one assignee, a description and a due date.
- Due dates must be reasonable.
- The assignee should receive a notification.

### CAPA-203 Escalate overdue actions
As a QA manager, I want overdue actions escalated, so CAPAs don't silently slip.
- Overdue actions are escalated to the manager.
- Escalations happen quickly.

### CAPA-204 Close a CAPA
As a QA manager, I want to close a CAPA only when all actions are done and evidence is attached.
- A CAPA cannot be closed while any action is open.
- Closing requires an effectiveness check plan, a closure summary of at least 50 characters and the QA manager's e-signature.
- The closure is recorded in the audit trail.

### CAPA-205 Edit a closed CAPA
As a CAPA owner, I want to edit a closed CAPA if I made a mistake.
- The owner can edit any field of a closed CAPA.

### CAPA-206 Effectiveness check
As QA, I want to check that the CAPA actually worked.
- The effectiveness check is performed after a suitable period.
- Results are approved.
- TBD: what happens if the CAPA was not effective.
