```yaml
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
```
