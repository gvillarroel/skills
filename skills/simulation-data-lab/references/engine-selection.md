# Engine selection

Choose the simplest paradigm that represents the mechanism capable of changing
the requested outcome. The common experiment and data contract is more
important than forcing every model into one library.

All choices below are engines for an offline mathematical representation, not
permission to run the system under study. Inspect supplied models for live
connectors before execution. Disable or replace hardware-in-the-loop,
production SDKs, target-program callbacks, remote simulation services, and real
model/tool calls with explicit mathematical mechanisms. If that substitution
would invalidate the intended model, report the limitation instead of running
the target. Local numerical engines are allowed; an engine name matching a
studied product does not authorize launching that product for measurement.

## Default routing

| System structure | Default | Use it when | Escalate when |
| --- | --- | --- | --- |
| Algebraic uncertainty, risk propagation, sampling, or independent trials | NumPy `Generator`, SciPy statistics, or plain Python for a dependency-free small model | State evolution and resource contention are not central | Use OpenTURNS for correlated inputs, rare-event reliability, calibration, or metamodels |
| Continuous state and rates of change | SciPy `solve_ivp` | ODEs, compartment models, aggregate populations, concentrations, or control states fit in Python | Use SciML when stiffness, SDE/DAE/DDE support, differentiability, GPU, or large ensembles justify Julia |
| Entities wait for scarce resources or follow a process | SimPy | Queues, service systems, logistics, manufacturing, inventory processes, or throughput | Use an existing enterprise DES model when its validated libraries and data are material |
| Heterogeneous actors interact through space, networks, memory, or local rules | Mesa | Agent identity and micro-to-macro emergence affect the outcome | Use Agents.jl for a Julia project or demonstrated scale bottleneck |
| Aggregate stocks, flows, delays, and feedback loops | Explicit stock-flow equations over SciPy | A new, compact system-dynamics model can be expressed transparently | Use PySD for a supplied Vensim `.mdl` or XMILE model; do not recreate it silently |
| Global sensitivity of an executable model | SALib as an experiment layer | Morris screening, Sobol, FAST, PAWN, or other supported designs fit their assumptions | Use OpenTURNS for dependence, reliability, surrogate, or richer UQ workflows |
| True DES + ABM + system-dynamics hybrid with a corporate visual model | Existing AnyLogic model | The license, model, and runtime are available and hybrid coupling is essential | Otherwise decompose the coupling explicitly and preserve interface variables |
| Control, embedded, or multidomain physical block model | Existing Simulink/Simscape model | The `.slx`/project and licensed products are already part of the task | Use FMI/FMUs for supported exchange or co-simulation rather than translating behavior by hand |
| Teaching or participatory ABM | NetLogo and BehaviorSpace | The interactive model or NetLogo ecosystem is itself a requirement | Export BehaviorSpace runs into the common tables for downstream analysis |

Do not choose an agent-based model merely because the domain contains people.
If people are exchangeable jobs competing only for capacity, a discrete-event
queue is simpler. Use ABM when heterogeneity, memory, topology, adaptation, or
local interaction changes the phenomenon.

## Why the default is Python-first

The default is a modular Python stack, not one monolithic engine. It provides a
transparent path from model code to tabular analysis, works headlessly, has
specialists for the main paradigms, and does not require a commercial license.
The bundled runner therefore orchestrates a narrow Python adapter while leaving
the inner engine open.

Before selecting an optional mathematical engine, check its local installation
metadata and exact version. Version probes may concern the numerical runtime,
not the emulated target's executable. Require headless offline execution.
Do not install a large dependency or change engines silently. For a small model,
use the Python standard library when it represents the mechanism faithfully; if
the required engine is unavailable and a fallback would change semantics,
deliver an executable plan and dependency list without fabricated results.

- [NumPy random generation](https://numpy.org/doc/stable/reference/random/)
  provides explicit generators and reproducible seed construction.
- [SciPy `solve_ivp`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.solve_ivp.html)
  solves initial-value ODE systems and exposes solver success and events.
- [SimPy](https://simpy.readthedocs.io/en/stable/) is a process-based
  discrete-event framework with resources and generator-defined processes.
- [Mesa](https://mesa.readthedocs.io/stable/) provides agent/model primitives,
  space, data collection, batch runs, and Python analysis integration.
- [SALib](https://salib.readthedocs.io/en/stable/) implements multiple global
  sensitivity designs; it is an overlay, not a simulation engine.
- [PySD](https://pysd.readthedocs.io/en/master/) translates Vensim or XMILE
  models and lets Python modify, run, and observe them.
- [OpenTURNS reliability and sensitivity](https://openturns.github.io/openturns/latest/theory/reliability_sensitivity/reliability_sensitivity.html)
  covers correlated sensitivity, threshold probabilities, FORM/SORM, importance
  sampling, subset simulation, and other advanced UQ methods.

## Criteria-based specialized choices

There is no universal winner:

- Python is the best general default for a portable agent-authored skill and
  analysis-ready output.
- Prefer [SciML ensembles](https://docs.sciml.ai/SciMLBase/stable/interfaces/Ensembles/)
  when difficult differential equations, specialized solver families, or
  high-performance trajectory ensembles outweigh the cost of a Julia runtime.
- Prefer [AnyLogic multimethod modeling](https://www.anylogic.com/features/)
  when a licensed, monolithic visual environment must combine DES, ABM, and
  system dynamics. Its licensing and project format make it a poor default
  dependency for a portable skill.
- [Simulink](https://www.mathworks.com/help/simulink/index.html) is preferable
  when an engineering organization already supplies an offline block or
  physical-domain mathematical model; exclude hardware and target-code execution.
- [NetLogo BehaviorSpace](https://ccl.northwestern.edu/netlogo/docs/behaviorspace.html)
  is excellent for approachable ABM parameter sweeps and classroom use.

## Selection checks

Before implementation, answer these questions:

1. What state changes, and is time continuous, stepped, or event-driven?
2. Do named entities and their interaction graph matter, or only aggregate
   counts and queues?
3. Is the uncertainty stochastic, parametric, structural, numerical, or a mix?
4. Does an existing validated model or file format have to remain authoritative?
5. What fidelity is needed to answer the estimand, rather than to imitate the
   whole system?
6. Can the engine run headlessly with explicit seeds and export every failed as
   well as successful run?
7. What local runtime, memory, license, or numerical-compute cost bounds apply?
8. Can every live connector, target callback, and hardware dependency be excluded?

Record the installed engine, solver, RNG, and library versions after execution;
do not write `latest` or `unknown` into provenance.
