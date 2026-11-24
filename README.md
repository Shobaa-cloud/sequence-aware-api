# Sequence-Aware API Misuse Detection

A small Flask API that checks the **order** of each user's API calls instead of judging every request on its own.
If a user asks for data before logging in, or logs out without ever logging in, the call is blocked and written to that user's log as `MISUSE`.

This repository is the working prototype of the idea in our paper:

> Packiyam, Sasiprabha V, Shobaa P, Srimukhi T G, Shreelinganaathan M.
> *Sequence Aware API Misuse Detection in Cloud Applications.* Zenodo, 2026.
> [doi.org/10.5281/zenodo.19710272](https://doi.org/10.5281/zenodo.19710272)

## Why the order of calls matters

Most API checks only ask "is this one request allowed?". Some misuse only shows up in the *sequence* of calls: a client that skips login and goes straight to a data endpoint, or a script that replays calls out of order.
This API keeps a small session state for every user and checks each call against the expected flow:

```
login  ──►  get_data (any number of times)  ──►  logout
```

Anything that breaks this flow is refused and logged.

## Endpoints

Every endpoint is a `POST` that takes a JSON body with the user's name: `{"user": "alice"}`.

| Endpoint | Allowed when | Normal response | Out-of-order response | Log entry |
|---|---|---|---|---|
| `/login` | always | `200` `{"user": "alice", "status": "logged in"}` | – | `login` |
| `/get_data` | the user is logged in | `200` `{"user": "alice", "data": "Here is your data"}` | `403` `{"error": "login required"}` | `get_data` or `MISUSE: get_data_before_login` |
| `/logout` | the user is logged in | `200` `{"user": "alice", "status": "logged out"}` | `400` `{"error": "not logged in"}` | `logout` or `MISUSE: logout_without_login` |

A request with no `user` field gets `400` `{"error": "user required"}` and is not logged.

## Run it

You need Python 3 and Flask.

```bash
git clone https://github.com/Shobaa-cloud/sequence-aware-api.git
cd sequence-aware-api
pip install -r requirements.txt
python app.py
```

The server starts on port `5000`. Set the `PORT` environment variable to use a different port.

## Try it

**curl** (Git Bash, Linux or macOS):

```bash
# 1. Misuse: ask for data before logging in  ->  403
curl -X POST http://localhost:5000/get_data -H "Content-Type: application/json" -d '{"user": "alice"}'

# 2. The normal flow  ->  200, 200, 200
curl -X POST http://localhost:5000/login    -H "Content-Type: application/json" -d '{"user": "alice"}'
curl -X POST http://localhost:5000/get_data -H "Content-Type: application/json" -d '{"user": "alice"}'
curl -X POST http://localhost:5000/logout   -H "Content-Type: application/json" -d '{"user": "alice"}'

# 3. Misuse: log out again without logging in  ->  400
curl -X POST http://localhost:5000/logout   -H "Content-Type: application/json" -d '{"user": "alice"}'
```

**PowerShell** (Windows):

```powershell
Invoke-RestMethod -Method Post -Uri http://localhost:5000/login -ContentType "application/json" -Body '{"user": "alice"}'
```

**Postman:** create a `POST` request to `http://localhost:5000/login`, then choose *Body → raw → JSON* and enter `{"user": "alice"}`.

## Logs

Each user gets a file at `logs/<user>.txt`, in the folder you started the server from. After the curl steps above, `logs/alice.txt` looks like this:

```
2026-11-24 11:50:49.594052 - MISUSE: get_data_before_login
2026-11-24 11:50:49.598970 - login
2026-11-24 11:50:49.600804 - get_data
2026-11-24 11:50:49.602616 - logout
2026-11-24 11:50:49.604237 - MISUSE: logout_without_login
```

## Project structure

```
sequence-aware-api/
├── app.py            # Flask API: per-user session state, sequence checks, logging
├── requirements.txt  # flask
└── logs/             # created when the server starts; one file per user
```

## Limitations

This is a prototype that demonstrates the sequence check itself:

- Sessions are kept in memory, so they reset when the server restarts and aren't shared between server processes.
- The `user` field is trusted as sent. There are no passwords or tokens yet, so this shows *sequence* checking, not authentication.
- The allowed order is hard-coded for three endpoints.
- Input validation is minimal.
- The evaluation reported in the paper is not part of this repository yet.

## Roadmap

- [ ] Replace the `user` field with real login tokens (for example JWT)
- [ ] Describe the allowed call order as a state machine, so new endpoints and rules are configuration instead of code
- [ ] Validate and sanitise the `user` value before using it
- [ ] Store sessions and logs in a database
- [ ] Add automated tests (pytest) and an evaluation script
- [ ] A small dashboard that lists `MISUSE` events per user
