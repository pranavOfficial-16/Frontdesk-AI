import os
import uuid
import torch
import logging
import firebase_admin

from dotenv import load_dotenv
from firebase_admin import credentials, firestore
from sentence_transformers import SentenceTransformer, util

from constants import KNOWLEDGE_BASE_DB, HELP_REQUESTS_DB
from constants import HELP_MESSAGE, THRESHOLD, SEMANTIC_MODEL
from constants import ID, QUESTION, ANSWER, STATUS, PENDING, EMPTY

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize the semantic model once
model = SentenceTransformer(SEMANTIC_MODEL)


load_dotenv()

FIREBASE_FILE_PATH = os.getenv("FIREBASE_FILE_PATH")

cred = credentials.Certificate(FIREBASE_FILE_PATH)
firebase_admin.initialize_app(cred)
db = firestore.client()


# check knowledge base for a semantically matching answer
def check_kb(question: str) -> str:
    logging.info(f"[Firebase] Checking KB for question: '{question}'")
    try:
        docs = list(db.collection(KNOWLEDGE_BASE_DB).stream())
        if not docs:
            logging.info("[Firebase] Knowledge base is empty")
            return HELP_MESSAGE, False

        kb_questions = [doc.to_dict().get(QUESTION, EMPTY) for doc in docs]
        kb_answers = [doc.to_dict().get(ANSWER, EMPTY) for doc in docs]

        # Encode question and KB questions
        question_emb = model.encode(question, convert_to_tensor=True)
        kb_embs = model.encode(kb_questions, convert_to_tensor=True)

        # Compute cosine similarity
        cosine_scores = util.cos_sim(question_emb, kb_embs)[0]
        max_score, idx = torch.max(cosine_scores, dim=0)

        # Threshold for semantic match
        if max_score >= THRESHOLD:
            answer = kb_answers[idx]
            logging.info(f"[Firebase] Semantic match found: '{answer}'")
            return answer, True
        else:
            logging.info("[Firebase] No semantic match found")
            return HELP_MESSAGE, False

    except Exception as e:
        logging.error(f"[Firebase] Error checking KB: {e}")
        return EMPTY, False


# Create a new help request
def create_help_request(question: str):
    try:
        request_id = str(uuid.uuid4())
        db.collection(HELP_REQUESTS_DB).document(request_id).set(
            {ID: request_id, QUESTION: question, ANSWER: EMPTY, STATUS: PENDING}
        )
        logging.info(
            f"[Firebase] Created help request '{request_id}' for question '{question}'"
        )
        return request_id
    except Exception as e:
        logging.error(f"[Firebase] Error creating help request: {e}")
        return None


# Delete all documents in help_requests
def delete_help_requests():
    try:
        help_docs = db.collection(HELP_REQUESTS_DB).stream()
        count_help = 0
        for doc in help_docs:
            db.collection(HELP_REQUESTS_DB).document(doc.id).delete()
            count_help += 1
        logging.info(f"[Firebase] Deleted {count_help} documents from help_requests")
    except Exception as e:
        logging.error(f"[Firebase] Error deleting help_requests: {e}")


# Delete all documents in knowledge_base
def delete_knowledge_base():
    try:
        kb_docs = db.collection(KNOWLEDGE_BASE_DB).stream()
        count_kb = 0
        for doc in kb_docs:
            db.collection(KNOWLEDGE_BASE_DB).document(doc.id).delete()
            count_kb += 1
        logging.info(f"[Firebase] Deleted {count_kb} documents from knowledge_base")
    except Exception as e:
        logging.error(f"[Firebase] Error deleting knowledge_base: {e}")
