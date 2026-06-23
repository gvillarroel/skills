# Bar Charts In Slidev

- **Data shape:** Use category objects with stable names and numeric fields for prior/current/future states.
- **Animation pattern:** Update bar heights from `$clicks` and reveal labels only when the final value state needs annotation. Use `universalTransition` when moving between related bar encodings.
- **Display guidance:** Keep category labels short and preserve order unless the slide explicitly tells a ranking story.
- **Modules:** Register `BarChart`, `GridComponent`, and `TooltipComponent`.
- **Pitfalls:** Avoid dynamic axis max values across clicks; changing scale can hide the actual magnitude of the animation.
