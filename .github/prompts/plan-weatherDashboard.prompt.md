## Architecture Diagram & Data Flow

---

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        BROWSER (Client)                      │
│                                                             │
│   ┌─────────────┐    ┌──────────────┐   ┌───────────────┐  │
│   │  index.html  │    │   style.css  │   │    app.js     │  │
│   │  (structure) │    │  (styling)   │   │  (fetch API)  │  │
│   └─────────────┘    └──────────────┘   └──────┬────────┘  │
│                                                 │            │
└─────────────────────────────────────────────────┼────────────┘
                                                  │
                               HTTP GET /api/weather?city=London
                                                  │
                                                  ▼
┌─────────────────────────────────────────────────────────────┐
│                     FLASK BACKEND (Server)                   │
│                                                             │
│   ┌──────────────────────────────────────────────────────┐  │
│   │                    app.py (Flask)                    │  │
│   │                                                      │  │
│   │   /api/weather  ──►  validate input                  │  │
│   │                       │                              │  │
│   │                       ▼                              │  │
│   │                  check cache ──► HIT ──► return JSON │  │
│   │                       │                              │  │
│   │                      MISS                            │  │
│   │                       │                              │  │
│   │                       ▼                              │  │
│   │              build OWM API request                   │  │
│   │         (inject API_KEY from env vars)               │  │
│   └──────────────────────────┬───────────────────────────┘  │
│                              │                               │
└──────────────────────────────┼───────────────────────────────┘
                               │
              HTTPS GET api.openweathermap.org/data/2.5/weather
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│               OpenWeatherMap API  (External)                 │
│                                                             │
│         Returns raw JSON: temp, humidity, wind,             │
│         condition codes, icons, forecast data               │
└─────────────────────────────────────────────────────────────┘
```

---

### Data Flow — Step by Step

```
1. USER INPUT
   User types "London" → clicks Search (or presses Enter)

2. FRONTEND → BACKEND  (HTTP Request)
   app.js sends:
   GET http://localhost:5000/api/weather?city=London

3. FLASK: INPUT VALIDATION
   - Strip and sanitize city param
   - Reject empty / suspicious input → return 400

4. FLASK: CACHE CHECK
   - Key: "weather:London"
   - HIT  → return cached JSON immediately (skip step 5)
   - MISS → proceed to step 5

5. FLASK → OPENWEATHERMAP  (External HTTP Request)
   GET https://api.openweathermap.org/data/2.5/weather
       ?q=London&appid={API_KEY}&units=metric

6. OPENWEATHERMAP → FLASK  (Raw Response)
   Returns full JSON payload:
   {
     "name": "London",
     "main": { "temp": 14.2, "humidity": 72 },
     "wind": { "speed": 5.1 },
     "weather": [{ "description": "light rain", "icon": "10d" }]
   }

7. FLASK: TRANSFORM & CACHE
   - Extract only needed fields
   - Store in cache with TTL (e.g., 10 minutes)
   - Return cleaned JSON to frontend

8. BACKEND → FRONTEND  (HTTP Response)
   {
     "city":        "London",
     "temperature": 14.2,
     "humidity":    72,
     "wind_speed":  5.1,
     "condition":   "light rain",
     "icon":        "10d"
   }

9. FRONTEND: RENDER
   app.js receives JSON → updates DOM elements with weather data
   Displays icon from: https://openweathermap.org/img/wn/10d@2x.png
```

---

### Key Design Decisions

| Concern | Decision |
|---|---|
| API key location | Server-side only, loaded from `.env` via `python-dotenv` |
| Caching | Flask-Caching (simple in-memory or Redis) with 10-min TTL |
| Error passthrough | Flask maps OWM 404 → client 404, OWM 5xx → client 503 |
| CORS | `flask-cors` restricts to frontend origin only |
| Data shaping | Flask filters OWM's large payload — frontend receives minimal clean JSON |
