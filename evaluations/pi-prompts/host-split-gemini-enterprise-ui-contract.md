Use the copied skill for Google Cloud Gemini Enterprise. Treat `skills/gemini-enterprise-ui/` as read-only. Write task artifacts only in this workspace outside the skill. Keep temporary state and caches task-local. Use only the supplied skill and normal local tools. Do not discover other skills or read installed host documentation, host examples, personal configuration, or any source outside this workspace. Running installed tool executables is allowed.

Create the deliverables directory and write deliverables/route.md first. Then execute the following exact bundled command as a standalone bash call, without prefixing other commands:

```bash
python skills/gemini-enterprise-ui/scripts/design_values.py --palette colorset1 --list-tokens > deliverables/design.json
```

Inspect the result and write `deliverables/route.md` recommending the appropriate UI route for Google Cloud Gemini Enterprise. Explain its actual transport/rendering boundary and the next host acceptance check. Do not install, deploy, or change any account settings.
