Use the read-only skill at skills/line-world-google-vids. Read ../prompt.md first.
Exercise the bundled narration_cues.py with project-owned JSON fixtures. Supply
one scene "split" starting at global audio second 40, ending at 60, duration20.
Its transcript words are 60 at47.37–48.00, 20 at48.27–48.60, y at48.60–48.85,
and 20 at48.85–49.70. Bind targets train, validation and test to phrases sesenta,
veinte occurrence1, and veinte occurrence2. Produce aligned.json using the
bundled CLI. Also verify the library rejects an unspoken phrase without
substituting an estimate; capture that expected rejection in rejection.json
using a successful wrapper process. Keep the skill unchanged. Required exact
outputs: aligned.json and rejection.json. No live Google Vids operations are
needed. Do not claim a local fixture was measured in a real editor.
