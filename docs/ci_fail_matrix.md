# CI Failure Matrix

| Test | Root Cause | Status | PR |
|------|------------|--------|----|
| tests/test_friction_factor.py::test_surface_zone_factor | Variable `car` used instead of parameter in `Track.base_friction_factor` | Fixed | this PR |
| tests/test_surface_friction.py::test_surface_zone_friction | Same as above causing NameError | Fixed | this PR |
