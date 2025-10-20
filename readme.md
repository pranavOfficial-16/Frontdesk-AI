## Frontdesk AI - Human-in-the-Loop System

An AI receptionist system that handles customer inquiries and escalates unknown questions to human supervisors, creating a self-learning knowledge base.

## Tech stack

- **LiveKit** - Real-time voice AI platform
- **Google gemini** - LLM model
- **AssemblyAI** - STT model
- **Firebase** - Cloud Real-time database
- **FastAPI** - Backend web framework for UI and firebase integration
- **HTML/Bootstrap** - Simple supervisor UI

## Getting Started

1. Create virtual environment

   ```bash
   python -m venv venv
   .\venv\bin\activate
   ```

2. Install dependencies

   ```bash
   pip install -r requirements.txt
   ```

3. Create .env file

   ```bash
   LIVEKIT_URL=
   LIVEKIT_API_KEY=
   LIVEKIT_API_SECRET=

   GOOGLE_API_KEY=

   FIREBASE_FILE_PATH=firebasekey.json file path
   ```

4. Download model files

   ```bash
   uv run agent.py download-files
   ```

5. Speak to your agent

   ```bash
   uv run agent.py console
   ```

6. Run Supervisor UI

   ```bash
   uvicorn main:app --reload
   ```

## Design Flow

- **Real-time Voice Pipeline**: LiveKit handles WebRTC streams → AssemblyAI for STT → Google gemini for LLM model
- **Separation of Concerns**: Voice agent, Supervisor UI, and Database is real-time
- **Unified Data Model**: Same document IDs across help_requests and knowledge_base collections for traceability
- **AI Agent**: function-based design where tools handle all external interactions

## Database Design

help_requests 

```bash
{
    "id": "uuid",           Primary key
    "question": "text",     Customer query
    "answer": "text",       Supervisor response
    "status": "pending"     Workflow state
}
```

knowledge_base

```bash
{
    "id": "same_uuid",      Links to original request
    "question": "text",     Canonical question
    "answer": "text",       Verified answer
    "status": "resolved"    Always resolved
}
```
