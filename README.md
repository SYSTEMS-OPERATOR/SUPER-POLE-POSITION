# 🏎️ SUPER-POLE-POSITION 🏁  
🔴🟡🟢 **AI RACING GYM – PUSH YOUR LIMITS!** 🟢🟡🔴  
_A Reinforcement Learning Lab for Next-Gen AI Racers_

## CI Badges
![tests](https://github.com/example/super-pole-position/actions/workflows/ci.yml/badge.svg)
![coverage](https://img.shields.io/badge/coverage-71%25-yellow)

🕹️ **INSERT COIN TO CONTINUE...**  
💾 **LOADING AI MODELS...**  
🚦 **READY? SET. GO!**

```
 rrr
rrrrr
 rrr
```

---

## 🎮 **ABOUT THE GAME**  
### 🏁 **WELCOME TO SUPER-POLE-POSITION!**  
🏎️ **A high-speed, AI-driven racing experience where intelligence meets the asphalt!**  
⚙️ **Designed as a Gymnasium-based RL training environment**, SUPER-POLE-POSITION lets AI models **compete, adapt, and evolve** in a simulated race track.  

🔹 **Classic NAMCO-inspired arcade physics**  
🔹 **Multi-agent reinforcement learning** 🏎️🏎️  
🔹 **Retro-styled toroidal tracks & infinite procedurally generated circuits**  
🔹 **Real-time AI benchmarking & strategy evaluation**

## Quick Start
```bash
pip install -r requirements.txt && python run_game.py
# or dive into the CLI
spp qualify --agent null --track fuji
# try the new curved Fuji circuit
spp qualify --agent null --track fuji_curve
# record scores under your initials
spp race --player AAA
# load a custom track
spp race --track-file my_track.json
```
![](docs.gif)


### Title Menu
Running with `--render` opens a simple title screen. Use the arrow keys to set
**difficulty**, toggle **audio**, choose a **track**, and adjust **volume**.
Press **Enter** to begin or **Esc** to quit.


🔥 **Only the fastest and smartest AIs survive. Are you ready to build the ultimate racing intelligence?** 🔥  

---

## 🚗 **HOW IT WORKS**  
- **🟢 SELECT YOUR AI DRIVER**  
  - GPT-based planners? ✅  
  - Reinforcement Learning agents? ✅  
  - Custom AI models? ✅  
  - All models welcome to the race!  

- **🔴 CHOOSE YOUR CIRCUIT**  
  - Toroidal maps? 🌀  
  - Procedural tracks? 🌎  
  - Chaos Mode? 🔥  

- **🟡 TRAIN & COMPETE!**  
  - Race your AI against itself, past iterations, or other models.  
  - Watch how strategies evolve over time.  
  - Track leaderboards & lap performance in real-time.  

---

## 🛠️ **FEATURES**
🎯 **AI Gymnasium:** Compete, train, and evolve AI models using real-time feedback.  
💾 **Logging & Benchmarking:** AI decision tracking, reaction times, and lap data stored for review.  
🎶 **Binaural Audio Racing:** Hear the speed—each AI’s performance mapped to immersive stereo audio.  
💡 **Autonomous Learning Mode:** Let AIs race, improve, and adapt without human intervention.  
🌀 **Toroidal Racing Physics:** No edges, no limits—just infinite speed.
🖼️ **Retro ASCII sprites** for cars, billboards and explosions.
🎨 **Placeholder PNGs** stored in `assets/sprites` for arcade-faithful builds.
These are zero-byte stubs included only so the file paths exist.
🚀 **Hyper Mode** for uncapped speed and obstacle chaos.
🕹️ **Arcade-accurate mechanics**: slipstream boost, off-road slowdown, crash penalties
🛞 **Two-speed gearbox with torque kick**
🪧 **Billboards shatter with time penalty**
🌱 **Dynamic friction zones**
🚗 **CPUCar opponents with blocking behaviour**
🌄 **Horizon sway & sprite scaling**
📻 **Engine pitch scales with RPM**
🎵 **Audio stubs** in `assets/audio` ready for replacement.

---

## 📜 **CONTROLS**
🕹️ **CAR 1:** _(Human or AI)_  
⬆️ **Throttle**  
⬇️ **Brake**  
⬅️➡️ **Steer Left / Right**
**Z/X** **Shift Down / Up**

Enable purist mode with `--no-brake` to disable braking entirely.

For more details see [GAMEPLAY_FAQ.md](GAMEPLAY_FAQ.md).

### 🖐️ Virtual Joystick
Install the `pygame-virtual-joystick` library to control the car on touchscreens.
Enable it with `--virtual-joystick` when launching a race or qualifying run:
```bash
spp race --render --virtual-joystick
```

### 🏁 Steering Wheels & Gamepads
Use the new `joystick` agent for analog input from a wheel or gamepad. Simply
connect your device and run:
```bash
spp race --render --agent joystick
```
Set `DISABLE_BRAKE=1` to race without a brake pedal for an authentic upright
cabinet challenge. Steering sensitivity can be tweaked via the `turn_rate`
entry in `config.arcade_parity.yaml`.

🕹️ **CAR 2:** _(AI-Driven)_
🤖 **Automated racing, planning, and learning**

📡 **Live Monitoring Mode** – Track AI behavior in real-time, with zero-latency logging.

---

## 🔧 **INSTALLATION & SETUP**
💾 **Requirements:**  
- 🖥️ Python 3.8+  
- 🏎️ Gymnasium (Reinforcement Learning framework)  
- 🧠 PyTorch / TensorFlow (for AI models)  
- 🎵 SimpleAudio or Pygame's mixer (optional, tests skip if absent)
- 🎮 Pygame (for optional graphics)
- 📡 ZeroMQ / WebSockets (for live AI telemetry)

🔽 **Install**
```bash
pip install -r requirements.txt
pip install -e .
```

For automated testing you can install the lighter CI requirements:
```bash
pip install -r requirements-ci.txt
```
If CUDA support is unavailable, skip the AI extras:
```bash
pip install -e .[graphics,audio]
```
This avoids importing heavy GPU libraries until you explicitly load the GPT planner.

### Assets
Placeholder PNG and WAV files live under `assets/sprites` and `assets/audio`.
No binary blobs are checked in. Use `generate_placeholders.py` inside each
folder to create simple stand-ins if you haven't supplied real artwork or
samples. See `assets/sprites/SPRITES.md` and `assets/audio/AUDIO.md` for the
full list.
For planned graphic enhancements consult [`GRAPHICS_FIDELITY_TASKS.md`](GRAPHICS_FIDELITY_TASKS.md).

🚀 **Run a Test Race**
```bash
super-pole-position
```

🏁 **AI-Only Mode**
```bash
super-pole-position --ai
```

📊 **Log & Monitor AI Performance**
```bash
super-pole-position --episodes 1
```

---

## 🏆 **LEADERBOARD**
👑 **Fastest AI Lap Times** _(Updated Automatically)_  
🏎️ **Rank | AI Name | Best Lap Time**  
1️⃣ 🔥 **TURBO-GPT** - 1:07.32  
2️⃣ 🏎️ **VELOCITY-VECTOR** - 1:09.84  
3️⃣ ⚡ **NEURAL-RACER-X** - 1:11.29

### Scoreboard API

Start a simple server (requires `fastapi`):

```bash
python -m super_pole_position.server.api
```

Use `GET /scores` to list results and `POST /scores` to submit new scores.
Set `--player AAA` when racing to record your initials.

To clear your local high-score table run:

```bash
python examples/reset_high_scores.py
```

### Scoreboard Sync Service

Keep your local scoreboard fresh with:

```bash
spp scoreboard-sync --host 127.0.0.1 --port 8000 --interval 30
```

---

## 🎶 **CREDITS & INSPIRATION**
- 🎮 **NAMCO’s Pole Position** _(1982)_ – The **arcade legend** that started it all.  
- 🏁 **F-Zero, Wipeout, Gran Turismo** – For the love of **speed and mastery.**  
- 💙 **You, the AI Researcher** – **For pushing intelligence to the limit.**  

---

## 🚦 **READY TO RACE?**
🎮 **PRESS START.**  
🕹️ **INSERT COIN.**  
🏎️ **HIT THE GAS.**  

🔥 **THE FUTURE OF AI RACING BEGINS NOW.** 🔥  

## What's new in v2
- Named track loading
- Traffic AI and crash logic
- HUD with audio
- Hyper mode for uncapped speed and performance metrics
- All original arcade mechanics recreated: slipstreaming, off-road slowdown, and timed checkpoints
- Try `--hyper` for a *next-gen AI challenge*
- Display performance metrics by setting `PERF_HUD=1`
- Mute background music via `--mute-bgm`

## 🎞️ Animated Sprite Demo
A small example using **Pygame 2** can be found in `examples/animated_sprite.py`.
Run it with:

```bash
python examples/animated_sprite.py
```

**Controls**

- Arrow keys – Move the sprite
- Esc – Quit the demo
- Use `--virtual-joystick` for touchscreen controls
- Use `--no-brake` for brake-free purist mode
- Select harder races with `--difficulty expert`

🚗 Happy racing! 🏁

For a code overview see [docs/GAME_FLOW.md](docs/GAME_FLOW.md).
