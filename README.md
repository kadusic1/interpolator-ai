# Agentic Numerical Interpolation

A full-stack chat-based interpolation app powered by LangGraph, FastAPI, and
React.

## Architecture

```mermaid
graph LR
    U[User] -->|interacts| FE[React Frontend]
    FE -->|HTTP/WebSocket| API[FastAPI + LangServe]
    API -->|invokes| A[LangGraph Agent]
    A -->|delegates| T[Tools]
    T -->|results| A
    A -->|response| API
    API -->|JSON| FE
    FE -->|renders| U

    subgraph Frontend
        FE
    end

    subgraph Backend
        API
        A
        subgraph Tools
            T1[Interpolation]
            T2[Visualization]
            T3[Export]
        end
    end
```

## Agent Workflow

```mermaid
flowchart TD
    A[User Input] --> B{Related to interpolation?}
    B -->|No| C[Reject & Explain]
    B -->|Yes| D[Parse Input]
    D --> E{Input Type}
    E -->|Function| F[Parse Function]
    E -->|Image| G[Extract Data]
    E -->|Data Points| H[Validate Points]
    F & G & H --> I[Call Interpolation Tool]
    I --> J[Display Results + Graph]
    J --> K{Continue?}
    K -->|Yes| A
    K -->|No| L[End / Export]
```

## Features

| Feature | Description |
|---------|-------------|
| Chat Interface | ChatGPT/Gemini-like experience |
| Input Parsing | Functions, images, raw data |
| Interpolation | Multiple numerical methods |
| Visualization | Interactive graphs |
| Export | PDF / Image output |
| Memory | Session-only (clears on close) |

## Agent Boundaries

| Agent Does | Agent Does NOT |
|------------|----------------|
| Parse user input | Perform calculations |
| Select appropriate tools | Store persistent memory |
| Format & explain results | Handle non-interpolation tasks |
| Route to visualization | Make mathematical decisions |

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React + TypeScript + Vite |
| API | FastAPI + LangServe |
| Agent | LangGraph |
| Validation | Pydantic |
| Visualization | Matplotlib |

## Quick Start

### Backend

```bash
# Setup virtual environment and install dependencies
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Start API server
uvicorn src.api.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend runs at `http://localhost:5173` and connects to the API at
`http://localhost:8000`.
