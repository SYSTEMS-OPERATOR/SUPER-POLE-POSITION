# 🧠 MIND.md — Decision Layer Map

This file documents the **thinking layer** of SUPER-POLE-POSITION:
the flow from CLI intent to game execution.

## 🧭 Dev Agent Breadcrumbs (Logic Flow)
1. Parse command-line intent in `super_pole_position/cli.py`.
2. Normalize runtime flags (`release`, audio, joystick, attract mode).
3. Route utility commands (`hiscore`, `reset-scores`, `scoreboard-sync`)
   before race logic starts.
4. Optionally launch menu for render runs and fold menu overrides into args.
5. Spin up `PolePositionEnv`, run an episode, and persist race artifacts:
   - leaderboard metrics
   - score table values
   - outro sequence

## 🎮 Core Intent Rules
- Keep behavior deterministic where practical.
- Prefer explicit mode routing (`qualify` vs `race`) over implicit state.
- Keep utility command handling isolated from gameplay loop setup.

