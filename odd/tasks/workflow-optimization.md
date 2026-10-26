Objective: optimize the two GitHub Actions workflows for speed and close the Sonar PR-gate gap. Branch: feat/workflow-optimization. Delivery: single PR to dev when done. Test runner: n/a (YAML workflow changes; verified by triggering a real run).

## Specs

S1. Add the same SonarCloud scan + quality-gate verification steps already in `main_muniguate-api.yml`'s `static-analysis` job as a new job in `pr-checks.yml`, so Sonar issues surface on the PR itself, not only after merge to `main`. (User: "agregar el mismo scan de Sonar + verificación de quality gate como un job más en pr-checks.yml, corriendo también en pull_request" — confirmed by user as "eso que me indicas".)

S2. Optimize `main_muniguate-api.yml` and `pr-checks.yml` for execution speed: parallelism, redundancy removal, whatever is warranted. (User: "validemos qué podemos modificar para que se realicen más rápido, paralelismo, optimización, validación de redundancias, etc, lo que consideres necesario.")

S3. Strategy for S2, per user's explicit choice (AskUserQuestion): "Velocidad máxima" — `build`, `unit-tests`, `static-analysis`, `api-tests` in `main_muniguate-api.yml` run in parallel (none actually depends on another's artifact except `deploy`, which needs `build`'s packaged artifact). `deploy` waits on all four; failure in any still blocks deploy exactly as before. Visual sequential chain in Actions UI is traded for wall-clock speed.

## Tasks

- T1 [S1]: static-analysis job in pr-checks.yml (Sonar scan + gate, pull_request trigger) — route: inline — status: done — commit: ccdf3a0
- T2 [S3]: restructure main_muniguate-api.yml job graph for max parallelism (split unit-tests into backend/frontend jobs, flatten needs graph, deploy needs all 4) — route: inline — status: done — commit: ccdf3a0
- T3 [S2]: add pip caching (actions/setup-python cache: pip) across all Python install steps in both workflows to cut redundant install time from the now-parallel/duplicated installs — route: inline — status: done — commit: ccdf3a0

## Log

L1 (2026-10-26, user, verbatim): "listo, te puse en dev, por favor trabajemos en una rama aparte, esta rama va a ser para optimización de los workflows, hagamos eso que me indicas y adicionalemnte validemos qué podemos modificar par aque se realicen más rápido, paralelismo, optimización, validación de redundancias, etc, lo que consideres necesario, siempre aplica el ODD que te instalé hace poco"

L2: Asked user (AskUserQuestion) whether to prioritize max speed (parallelize everything with no real artifact dependency) vs strict visual order vs hybrid. User chose "Velocidad máxima (recomendado)".

L3: Reviewed both workflow files in full. Confirmed via `grep` that only `deploy` in main_muniguate-api.yml actually consumes another job's output (`build`'s uploaded artifact via download-artifact). `unit-tests`, `static-analysis`, `api-tests` each independently install/checkout and don't read anything `build` produces — safe to flatten `needs:` so all four run concurrently, with `deploy` gated on all four (functionally identical blocking behavior, since GitHub Actions `needs:` requires every listed job to succeed regardless of whether they ran serially or in parallel).

L4: Did not touch branch protection required-status-check settings (whether the new pr-checks.yml Sonar job becomes a *required* blocking check) — out of scope for this request, flagged as a follow-up decision for the user.
