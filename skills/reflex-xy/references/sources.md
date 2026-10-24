# Verified upstream sources

Checked on 2026-10-24. The skill's executable baseline is the published
`xy==0.0.8` Windows wheel, exercised with Python 3.14.7. Python metadata requires
3.11+. This is a baseline, not a claim to be the latest version indefinitely.

- [Release v0.0.8](https://github.com/reflex-dev/xy/releases/tag/v0.0.8), published
  2026-10-13; tag commit `6483032a7947e1f44ced1a560ac08f1025637529`.
- [Release package metadata](https://github.com/reflex-dev/xy/blob/6483032a7947e1f44ced1a560ac08f1025637529/pyproject.toml).
- [Public Python exports](https://github.com/reflex-dev/xy/blob/6483032a7947e1f44ced1a560ac08f1025637529/python/xy/__init__.py).
- [Chart components and signatures](https://github.com/reflex-dev/xy/blob/6483032a7947e1f44ced1a560ac08f1025637529/python/xy/components.py).
- [Export behavior](https://github.com/reflex-dev/xy/blob/6483032a7947e1f44ced1a560ac08f1025637529/docs/guides/display-and-export.md).
- [Reflex integration](https://github.com/reflex-dev/xy/blob/6483032a7947e1f44ced1a560ac08f1025637529/docs/integrations/reflex.md).
- [Matplotlib compatibility](https://github.com/reflex-dev/xy/blob/6483032a7947e1f44ced1a560ac08f1025637529/docs/integrations/matplotlib.md).
- [Current official documentation](https://reflex.dev/docs/xy/).

Research also inspected main commit
`d95f84b6d61a6524d9af3f7879ba444dab095ae9` (2026-10-23), especially the data,
interaction, performance, export and CSP guides. Confirm newly documented
features against the installed release before using them.

The installation page at that revision still describes the 0.0.1 upload,
including absent Windows wheels and an old source-client build assumption.
Do not interpret that as the current release matrix. Check package-index wheel
availability for the actual Python/platform combination. Released wheels bundle
the native backend and render client. Source installs have separate Rust/client
build prerequisites; use the matching revision's build hook/guide.

This bundle contains original task-focused guidance and examples rather than a
vendored copy of upstream. XY's upstream license is Apache-2.0. No runtime
dependency on this repository or on a sibling skill is required.
