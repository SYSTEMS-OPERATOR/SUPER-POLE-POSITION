# SOPHY Coding Guide

Welcome, SOPHY! This document sets the tone for development.
It describes how to structure code and commits while also
highlighting design goals for achieving authentic Pole
Position parity.

## Coding Style
- Follow **PEP8** for all Python code.
- Adopt type hints throughout the codebase.
- Break logic into small, reusable functions.
- When naming functions or variables, prefer playful,
  memorable names where appropriate.
- Use intuitive emojis in documentation to highlight
  sections or direct flow.
- Document modules and functions with concise docstrings.

## Design Principles
- Aim for faithful reproduction of the original **Pole
  Position** look and feel.
- Keep modules loosely coupled so physics, UI and AI can
  evolve independently.
- Embrace test-driven development for all new features.
- Prefer dataclasses for structured data and maintain
  deterministic logic so replays are reproducible.
- Assets should load from `/assets` with sensible fallbacks
  for missing files.

## Gameplay Goals
- Maintain raster resolution of 256×224 with optional
  scanline effects.
- Provide crash animations, slipstream boost, off-road
  slowdown and timed checkpoints.
- Support stereo engine audio that pans with car position.
- Include a high-score table via the scoreboard API.
- Ensure tracks match Fuji Speedway and other classics.

## Commit Guidelines
- Write commit messages in present-tense imperative.
- Keep each commit focused on a single topic with a clear
  subject line (<50 characters) and an optional body.
- Reference related issues where relevant.

## Testing
Run the following before committing:

```bash
python -m py_compile $(git ls-files '*.py')
python -m pytest -q
```

Feel free to expand these checks as the project evolves.

Hi SOPHY! 👋
