#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Promote independently paraphrased, host-scoped craft lessons from source review."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
NAMES = ["desktop-plugin-ui", "desktop-chat-plugin-ui", "code-native-plugin-ui", "pi-extension-ui", "codex-plugin-ui", "chatgpt-desktop-plugin-ui", "gemini-enterprise-ui"]
CONTENTS = """## Contents

- [Relevance gate](#relevance-gate)
- [Taxonomic comparison](#compare-a-taxonomic-ambiguity)
- [Return to the agent](#return-control-to-the-agent)
- [Terminal presentation](#semantic-terminal-presentation)
- [Focused craft](#focused-craft-pass)
- [Acceptance](#acceptance)
- [Host adapter](#host-adapter)

"""
LESSONS = """## Focused craft pass

Choose the surface's purpose before applying a style: an agent decision is a
working/reading interaction. Preserve familiar host controls and established
identity. Typography, palette and density support the decision; a visual theme
does not justify extra navigation, ornamental controls or a new workflow.

Review the decision path and visual hierarchy before reading mechanical
findings. Record the most consequential issues first, then verify computed
geometry/contrast/focus and reconcile disagreements. A clean detector result
establishes only its checks. Rank blocked or misleading outcomes before state
coverage, hierarchy/readability and cosmetic polish. Keep the pass scoped to
the actual component; no new project-context system is required for a small fix.

Separate the subject/data role from active selection, action and status. Avoid
spending the primary-action fill on repeated diagram emphasis. Weight, outline,
position and labels can identify a disputed concept without implying danger or
preference. Retain semantic native roles and pair them with non-color cues.
Preserve confirmed palettes; categorical font/color/card bans are heuristics,
not reasons to override a host or a meaningful diagram node.

Group related information with proximity and spacing before adding frames.
Keep genuinely separate choice targets bounded and compare them consistently.
Use a small, deliberate set of type/spacing roles and preserve the host's font.
For ordinary web reading, start from the browser's 1rem body size; justify dense
diagram labels by their actual reading task and measured size. Test user text
scaling, wrapping and fallback fonts. If labels no longer fit, use an equivalent
text/tree representation instead of shrinking them to satisfy a fixed diagram.

Name the selected object in the primary action when it makes the consequence
clearer. Keep terminology consistent through pending, recorded and delivered
states. Refine default, pointer, keyboard, disabled and error states without
adding a confirmation or animation just to make the polish visible.

These lessons are an independent paraphrase from Impeccable's pinned
[distill](https://github.com/pbakaus/impeccable/blob/b4bff1626c344067788c2679f048a20057c7cc5a/skill/reference/distill.md),
[colorize](https://github.com/pbakaus/impeccable/blob/b4bff1626c344067788c2679f048a20057c7cc5a/skill/reference/colorize.md),
[typeset](https://github.com/pbakaus/impeccable/blob/b4bff1626c344067788c2679f048a20057c7cc5a/skill/reference/typeset.md),
and [polish](https://github.com/pbakaus/impeccable/blob/b4bff1626c344067788c2679f048a20057c7cc5a/skill/reference/polish.md)
references (reviewed 2026-11-12). They do not require that package, its detector,
or its command workflow; the actual host contract remains authoritative.

"""

def main():
    for name in NAMES:
        p = ROOT / f"skills/{name}/references/micro-decisions.md"
        text = p.read_text(encoding="utf-8")
        if "## Focused craft pass" in text:
            raise RuntimeError(f"Lessons already promoted: {name}")
        text = text.replace("## Acceptance\n", LESSONS + "## Acceptance\n")
        text = text.replace("## Relevance gate\n", CONTENTS + "## Relevance gate\n")
        p.write_text(text, encoding="utf-8", newline="\n")
    print("Promoted focused craft lessons to seven independent UI references.")

if __name__ == "__main__":
    main()
