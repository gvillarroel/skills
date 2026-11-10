# Authoring gate for a separate native verifier

Use the installed harbor-author-evaluation-datasets skill. An evaluation dataset is about to be sealed for a paid model run. The task uses Linux Docker with a separate verifier container and grades the actor's report.json. The author ran a reference Python checker directly on the host, got full credit, and built the actor's Docker image. The execution path from the native Harbor task to its separate verifier has yet to be exercised. The task files were authored on Windows and pushed to a Linux runner.

Decide whether the study may release model inference on this evidence. Describe the last pre-seal check that a different author can actually reproduce, the observations that must succeed in that check, and how to classify a missing evaluator resource if that check fails. State the commands or native actions only to the extent justified by the scenario. Produce one file named preflight-decision.json at the workspace root, with exactly these four fields:

- release_now, a boolean
- next_check, a nonempty string
- required_observations, a nonempty list of concrete strings
- failure_handling, a nonempty string

This is an authoring decision. Use the supplied facts and skill only. Do not start a model evaluation, access the network, or create a task bundle.
