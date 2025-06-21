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

Scores are stored in `scores.json` inside the package directory unless the
`SPP_SCORES` environment variable points to a different file.

## 📝 Example usage

```bash
curl http://127.0.0.1:8000/scores
curl -X POST http://127.0.0.1:8000/scores \
  -H "Content-Type: application/json" \
  -d '{"name":"TurboGPT","score":1200}'
```

🏁
