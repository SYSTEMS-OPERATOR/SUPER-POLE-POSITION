# 🫀 BODY.md — Runtime Systems Map

This file captures the **execution body** of the project: physics, rendering,
audio, and persistence systems that animate the game loop.

## 🧩 Subsystems
- **Physics:** track projection, car dynamics, collision and off-road handling.
- **Rendering:** pseudo-3D road projection, horizon, sprites, scanline options.
- **Audio:** engine loop, crash cues, menu and race feedback.
- **Persistence:** score files, leaderboard snapshots, parity artifacts.

## 🧭 Dev Agent Breadcrumbs (Frame Lifecycle)
1. Environment `reset()` seeds deterministic run state.
2. Agent action enters `step(action)`.
3. Physics updates speed, lane position, and hazards.
4. UI/HUD pulls canonical state snapshot for rendering.
5. Metrics + scoring update at lap/checkpoint boundaries.
6. Episode finalization writes score and evaluation outputs.

## ✅ Maintenance Rules
- Keep each subsystem loosely coupled for easy parity upgrades.
- Add tests for every behavior change in physics/UI/audio paths.
- Use small, typed helpers to preserve readability and PEP8 alignment.

