import os
import uuid
import logging
import firebase_admin

from dotenv import load_dotenv
from firebase_admin import credentials, firestore

# Configure logging
logging.basicConfig(level=logging.INFO)

load_dotenv()

FIREBASE_FILE_PATH = os.getenv("FIREBASE_FILE_PATH")

cred = credentials.Certificate(FIREBASE_FILE_PATH)
firebase_admin.initialize_app(cred)
db = firestore.client()


# Check knowledge base if the answer exists
def check_kb(question: str) -> str:
    logging.info(f"[Firebase] Checking KB for question: '{question}'")
    try:
        docs = (
            db.collection("knowledge_base").where("question", "==", question).stream()
        )
        for doc in docs:
            answer = doc.to_dict().get("answer", "")
            logging.info(
                f"[Firebase] Found KB entry for question '{question}': '{answer}'"
            )
            return answer
        logging.info(f"[Firebase] No KB entry found for question '{question}'")
        return ""
    except Exception as e:
        logging.error(f"[Firebase] Error checking KB: {e}")
        return ""


# Create a new help request
def create_help_request(question: str):
    try:
        request_id = str(uuid.uuid4())
        db.collection("help_requests").document(request_id).set(
            {"id": request_id, "question": question, "answer": "", "status": "pending"}
        )
        logging.info(
            f"[Firebase] Created help request '{request_id}' for question '{question}'"
        )
        return request_id
    except Exception as e:
        logging.error(f"[Firebase] Error creating help request: {e}")
        return None


# Add resolved Q&A to knowledge base
def add_to_kb(question: str, answer: str):
    try:
        kb_id = str(uuid.uuid4())
        db.collection("knowledge_base").add(
            {"id": kb_id, "question": question, "answer": answer, "status": "resolved"}
        )
        logging.info(
            f"[Firebase] Added KB entry '{kb_id}' for question '{question}' with answer '{answer}'"
        )
    except Exception as e:
        logging.error(f"[Firebase] Error adding to KB: {e}")


# Resolve help request and update knowledge base
def resolved_request(request_id: str, answer: str):
    try:
        req_ref = db.collection("help_requests").document(request_id)
        doc = req_ref.get()
        if not doc.exists:
            logging.warning(f"[Firebase] Help request '{request_id}' does not exist")
            return
        question = doc.to_dict()["question"]
        req_ref.update({"status": "resolved", "answer": answer})
        logging.info(
            f"[Firebase] Resolved help request '{request_id}' with answer '{answer}'"
        )
        add_to_kb(question, answer)
    except Exception as e:
        logging.error(f"[Firebase] Error resolving request '{request_id}': {e}")


# Delete all documents in help_requests
def delete_help_requests():
    try:
        help_docs = db.collection("help_requests").stream()
        count_help = 0
        for doc in help_docs:
            db.collection("help_requests").document(doc.id).delete()
            count_help += 1
        logging.info(f"[Firebase] Deleted {count_help} documents from help_requests")
    except Exception as e:
        logging.error(f"[Firebase] Error deleting help_requests: {e}")


# Delete all documents in knowledge_base
def delete_knowledge_base():
    try:
        kb_docs = db.collection("knowledge_base").stream()
        count_kb = 0
        for doc in kb_docs:
            db.collection("knowledge_base").document(doc.id).delete()
            count_kb += 1
        logging.info(f"[Firebase] Deleted {count_kb} documents from knowledge_base")
    except Exception as e:
        logging.error(f"[Firebase] Error deleting knowledge_base: {e}")
