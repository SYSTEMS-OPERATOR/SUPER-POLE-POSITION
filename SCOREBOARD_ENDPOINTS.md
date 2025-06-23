# 📈 Scoreboard API 🏆

This project exposes a minimal HTTP API for retrieving and submitting scores.
The API is optional and requires `fastapi` to be installed.

## 🚀 Start the server

```bash
python -m super_pole_position.server.api
```

The server will listen on `127.0.0.1:8000` by default.

## ⚡ Endpoints

- `GET /scores` – return the current scoreboard as JSON.
- `POST /scores` – submit a JSON body `{"name": "AI", "score": 123}` to add a
  new score.
- `GET /laps` – return the best lap times as JSON.
- `POST /laps` – submit a JSON body `{"name": "AI", "lap_ms": 42000}` to add a
  new lap time.

Scores are stored in `scores.json` and lap times in `lap_times.json` inside the
package directory unless the `SPP_SCORES` or `SPP_LAPS` environment variables
point to alternate files.

## 📝 Example usage

```bash
curl http://127.0.0.1:8000/scores
curl -X POST http://127.0.0.1:8000/scores \
  -H "Content-Type: application/json" \
  -d '{"name":"TurboGPT","score":1200}'
curl http://127.0.0.1:8000/laps
curl -X POST http://127.0.0.1:8000/laps \
  -H "Content-Type: application/json" \
  -d '{"name":"TurboGPT","lap_ms":42000}'
```

🏁
