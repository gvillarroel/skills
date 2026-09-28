# Boundary: ambiguous follow-up

Use the supplied skill as a read-only resource. Stay inside this isolated
workspace; do not read external local files or other skills. This task requires
no network or video download.

The conversation contains two offered candidates with no selected or recommended
one: option 1 is Women Astronauts Training / shot_050; option 2 is The President
Accounts / shot_094. The user says, “Descárgalo.”

Write your next Spanish reply in `reply.md`. Write `decision.json` with boolean
fields `download_performed` and `needs_selection` and a short English reason.
Handle the ambiguity without selecting or downloading either candidate. Do not
ask for permission to download; only resolve which candidate the user means.
