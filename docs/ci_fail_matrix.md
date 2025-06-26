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
```
