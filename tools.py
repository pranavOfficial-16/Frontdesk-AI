import logging

from firebase import check_kb, create_help_request
from livekit.agents import RunContext, function_tool

logging.basicConfig(level=logging.INFO)


@function_tool
async def help_request_tool(ctx: RunContext, question: str) -> str:
    """
    Handles all unknown questions and create help request to supervisor when it is not available in KB
    """
    question = question.lower()
    try:
        answer, valid = check_kb(question)
        if valid:
            return answer
        else:
            request_id = create_help_request(question)
            logging.info(f"[AI] Created help request with ID: {request_id}")
            return answer

    except Exception as e:
        logging.error(f"[AI] Error in help_request_tool: {e}")
        return ""
