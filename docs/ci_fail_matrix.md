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
