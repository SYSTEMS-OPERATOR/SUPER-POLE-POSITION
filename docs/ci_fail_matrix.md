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
```
