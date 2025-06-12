# Benchmarks

This directory stores episode logs generated during gameplay. Logs are organized
by UTC date so results from different runs remain separated.

For each completed episode two files are written:

- `<timestamp>.json` – summary metrics such as reward, lap times and timing stats.
- `<timestamp>-steps.csv` – per-step data capturing car positions, speeds and rewards.

These files are produced automatically by `super_pole_position.evaluation.logger`
and are useful for tracking historical performance.
