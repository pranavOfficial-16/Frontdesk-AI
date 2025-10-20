import logging

from livekit.agents import function_tool, RunContext
from firebase import check_kb, create_help_request

logging.basicConfig(level=logging.INFO)


@function_tool
async def help_request(ctx: RunContext, question: str) -> str:
    """
    After saying "Let me check with my supervisor and get back to you shortly." execute this function
    If you don't know the answer to a question try this function

    Args:
        question (str): The unknown question.
    """
    question = question.lower()
    try:
        logging.info(f"[AI] Received question: '{question}'")

        # Check knowledge base
        answer = check_kb(question)
        if answer:
            logging.info(f"[AI] Found answer in KB: '{answer}'")
            return answer  # if exists AI answers directly

        # Unknown -> create help request
        request_id = create_help_request(question)
        logging.info(f"[AI] Created help request with ID: {request_id}")

        # Step 3: Notify supervisor (simulated)
        logging.info(f"[Supervisor Notification] Please answer question: '{question}'")

        # Step 4: Return empty string -> AI escalates to human
        return ""

    except Exception as e:
        logging.error(f"[AI] Error in help_request: {e}")
        return ""
