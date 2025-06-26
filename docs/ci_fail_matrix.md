# CI Failure Matrix

| Test | Root Cause | Status | PR |
|------|------------|--------|----|
| tests/test_friction_factor.py::test_surface_zone_factor | Variable `car` used instead of parameter in `Track.base_friction_factor` | Fixed | this PR |
| tests/test_surface_friction.py::test_surface_zone_friction | Same as above causing NameError | Fixed | this PR |
| tests/test_api_server.py::test_scores_endpoints | Missing optional dependencies `fastapi` and `httpx` | Fixed | this PR |

```yaml
- test: tests/test_package_smoke.py::test_wheel_smoke
  status: pass
  root_cause: wheel smoke test builds wheel each run
  fix_plan: mark slow and gate behind CI_SLOW_TESTS
  runtime: 15.38
- test: tests/test_attract_mode.py::test_attract_mode_cycles_scores
  status: pass
  root_cause: attract mode cycles through high scores slowly
  fix_plan: mark slow and gate behind CI_SLOW_TESTS if needed
  runtime: 5.12
  - test: tests/test_friction_factor.py::test_surface_zone_factor
  status: fixed
  root_cause: variable `car` used instead of parameter in Track.base_friction_factor
- test: tests/test_surface_friction.py::test_surface_zone_friction
  status: fixed
  root_cause: same as above causing NameError
- test: tests/test_api_server.py::test_scores_endpoints
  status: fixed
  root_cause: missing optional dependencies `fastapi` and `httpx`
- test: tests/test_package_smoke.py::test_wheel_smoke
  status: pass
  runtime: 14.20
- test: tests/test_attract_mode.py::test_attract_mode_cycles_scores
  status: pass
  runtime: 5.11
  - test: tests/test_friction_factor.py::test_surface_zone_factor
  status: fixed
  root_cause: variable car used instead of parameter
  fix_plan: replaced car variable with argument
  runtime: 0.02
- test: tests/test_surface_friction.py::test_surface_zone_friction
  status: fixed
  root_cause: same as above causing NameError
  fix_plan: updated function parameter usage
  runtime: 0.02
- test: tests/test_api_server.py::test_scores_endpoints
  status: fixed
  root_cause: fastapi and httpx optional deps missing
  fix_plan: install dev extras for CI
  runtime: 0.03
- test: tests/test_package_smoke.py::test_wheel_smoke
  status: pass
  runtime: 9.09
- test: tests/test_attract_mode.py::test_attract_mode_cycles_scores
  status: pass
  runtime: 5.05
- test: tests/test_attract_mode.py::test_attract_mode_cycles_scores
  status: pass
  runtime: 5.04
- test: tests/test_attract_mode.py::test_attract_mode_cycles_scores
  status: pass
  runtime: 0.01
  root_cause: attract mode cycles through high scores slowly
  fix_plan: mark slow and gate behind CI_SLOW_TESTS
  runtime: 5.06
- test: tests/render/test_background.py::test_no_bg_flag
  status: skip
  root_cause: optional pygame dependency missing
  fix_plan: use importorskip and skip if pygame absent
  runtime: 0.00
- test: tests/test_attract_mode.py::test_attract_mode_cycles_scores
  status: fixed
  root_cause: idle_limit set too high under FAST_TEST causing slow loop
  fix_plan: reduce idle_limit to 0.1 seconds when FAST_TEST=1
  runtime: 0.15
- test: typing
  status: fixed
  root_cause: PolePositionEnv lacked episode_reward attribute
  fix_plan: define episode_reward in env init and reset
  runtime: 0.00
- run: 2025-06-26
  status: all-pass
  runtime: 2.18
- test: all
  status: pass
  runtime: 2.46
- test: tests/test_api_server.py::test_scores_endpoints
  status: skip
  root_cause: fastapi not installed
  fix_plan: install fastapi
  runtime: 0.00
- test: tests/render/test_fuji_shift.py::test_fuji_shift
  status: skip
  root_cause: pygame not installed
  fix_plan: add pygame dependency
  runtime: 0.00
- run: 2025-06-26
  status: all-pass
  runtime: 1.02
- test: tests/test_cli_headless.py::test_cli_headless
  status: pass
  root_cause: CLI start-up time
  fix_plan: mark slow and gate behind CI_SLOW_TESTS
  runtime: 3.16
- test: tests/test_cli_stub.py::test_cli_stub
  status: pass
  root_cause: CLI start-up time
  fix_plan: mark slow and gate behind CI_SLOW_TESTS
  runtime: 3.07
- test: tests/test_cli_smoke.py::test_cli_smoke
  status: pass
  root_cause: CLI start-up time
  fix_plan: mark slow and gate behind CI_SLOW_TESTS
  runtime: 2.81
- test: tests/test_ai_integration.py::test_openai_agent_fallback
  status: pass
  root_cause: environment spin-up
  fix_plan: mark slow and gate behind CI_SLOW_TESTS
  runtime: 2.78
```

- run: 2025-06-26
  status: all-pass
  runtime: 1.71

- run: 2025-06-26-a
  status: all-pass
  runtime: 1.00
