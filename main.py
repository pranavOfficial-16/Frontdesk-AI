import os
import logging
import firebase_admin

from fastapi import FastAPI
from dotenv import load_dotenv
from fastapi.params import Form
from fastapi.requests import Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from firebase_admin import credentials, firestore

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

load_dotenv()

FIREBASE_FILE_PATH = os.getenv("FIREBASE_FILE_PATH")

cred = credentials.Certificate(FIREBASE_FILE_PATH)
firebase_admin.initialize_app(cred)
db = firestore.client()


# Configure logging
logging.basicConfig(level=logging.INFO)


# Render the supervisor UI
@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    # Get first collection -> help_requests
    help_requests_docs = db.collection("help_requests").stream()
    help_requests = [{"id": doc.id, **doc.to_dict()} for doc in help_requests_docs]

    # Get second collection -> knowledge_base
    knowledge_base_docs = db.collection("knowledge_base").stream()
    knowledge_base = [doc.to_dict() for doc in knowledge_base_docs]

    # Send both collections to the template
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "help_requests": help_requests,
            "knowledge_base": knowledge_base,
        },
    )


# Resolve a help request
@app.post("/resolve_request")
async def resolve_request(id: str = Form(...), answer: str = Form(...)):
    try:
        if not answer.strip():
            return JSONResponse({"error": "Answer cannot be empty"}, status_code=400)

        doc_ref = db.collection("help_requests").document(id)
        doc = doc_ref.get()

        if not doc.exists:
            return JSONResponse({"error": "Document not found"}, status_code=404)

        # Get the question before updating
        doc_data = doc.to_dict()
        question = doc_data.get("question", "")

        if not question:
            return JSONResponse(
                {"error": "Question not found in document"}, status_code=400
            )

        logging.info(f"[Supervisor] Resolved question and answer'")
        logging.info(f"[Supervisor] Question: {question}")
        logging.info(f"[Supervisor] Answer: {answer}")

        # Update the help request document
        doc_ref.update(
            {
                "status": "resolved",
                "answer": answer,
            }
        )

        # Add to knowledge base using the SAME ID
        db.collection("knowledge_base").document(id).set(
            {
                "id": id,  # Use the same ID
                "question": question,
                "answer": answer,
                "status": "resolved",
            }
        )

        return JSONResponse({"message": "Request resolved successfully"})

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
