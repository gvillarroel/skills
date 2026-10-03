# Diagram composition release acceptance

Evaluate all repetitions, including failures. Runtime isolation and artifact
checks are separate gates. A final `ok` field alone is not sufficient.

## Shared observable requirements

- Exact requested output paths exist and contain the declared medium.
- Canvas and display dimensions match the prompt, with the requested essential
  label size at actual display scale (allow subpixel rounding, not deliberate shrinkage).
- Panels answer separate questions and form one explanation. Their array order,
  grid allocation, chosen forms, and relationship meanings agree with the figure.
- Native vector artwork remains self-contained. IDs and local references remain
  unambiguous. Repeat icon identities consistently and make unfamiliar symbols
  understandable through visible keys and accessible text.
- Imported source hashes match the report; the isolated skill bundle is unchanged.
- Independent browser re-audit finds no label overflow/collision or external load.
- Inspect every final screenshot at its actual dimensions. Check text/mark
  contrast, intended reading order, relationship endpoints, crossings, and lost
  facts. Inspect clipped marks rather than accepting or rejecting them blindly.
- A final audit without inspection mode must run after the final composition.
  Reports and screenshots must correspond to the final SVG, verified by hash.

## Case semantics

| Case | Independent semantic checks |
| --- | --- |
| Contract | Three peers around a library; read/write comparison; library inside service; two connections terminate on the intended synthesis objects. |
| Naturalistic | Editor, assistant, CI are unordered peers linked to shared workspace. Permissions preserve read/write source for editor, read/propose for assistant, read/publish results for CI. Human review precedes proposals becoming source. Source/build results containment is explicit. Upper/lower left spans and tall right synthesis are exact. |
| Generalization | Grains contain oats/barley and legumes contain peas/beans. Real borrow/grow/keep/return recurrence includes inspection before shelving. Kept and returned portions remain distinct without invented measures. Two comparison dimensions and exact group colors are preserved. Portrait layout fits. |
| Boundary | Copilot and cloud stay unresolved exact names. No substituted real-brand logos, permission facts, direction, or inferred product identities. Known connectivity and unknown permissions remain distinguishable. Useful complete figure and uncertainty review are delivered. |
| Fresh transfer | Digital contains cameras/audio recorders; optical contains lenses/binoculars. Checkout/use/return/clean/inspect/store repeats in that order. All equipment returns: no retained portion. Yellow/padded and purple/rigid dimensions are preserved without measures or quality claims. |

The release uses one contract, three naturalistic, three generalization, and one
boundary run, all fresh. Naturalistic/generalization require at least two of three
joint strict-and-artifact passes. Routing control uses only descriptions, without
forcing a skill; it is not proof of native app discovery. Source-renderer import
and real-logo integration are separately reviewed local checks.
