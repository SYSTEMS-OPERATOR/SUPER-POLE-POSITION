# 🎯 Parity Audit Quick-Start

Run the minimal auditor to capture frame and audio hashes from a short episode.
It will create a baseline on first run and compare subsequent runs against it.

```bash
python tools/parity_audit.py --seed 42 --frames 200 --audio 5 --dump parity_run.json
```

Check `parity_run.json` for metrics:
- `physics_delta` – lap time difference in seconds
- `render_similarity` – fraction of matching frame hashes
- `audio_similarity` – fraction of matching audio hashes

Use `--baseline <file>` to specify a golden baseline and `--strict` to fail when
deltas exceed thresholds.

## 🔬 Extended analysis checklist
- Add an SSIM pass over rendered frames and store aggregate drift values.
- Add FFT-based spectral distance for audio clips to complement hash matching.
- Track per-section drift windows (start grid, mid-lap, finish sequence) to
  localize parity regressions quickly.
