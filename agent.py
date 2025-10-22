from dotenv import load_dotenv
from tools import help_request_tool

from livekit import agents
from livekit.plugins import google
from livekit.agents import AgentSession, Agent, RoomInputOptions

from constants import INIT_MAIN, MODEL_TEMPERATURE
from constants import AGENT_INSTRUCTION, SESSION_INSTRUCTION, AGENT_VOICE

from firebase import delete_help_requests, delete_knowledge_base


load_dotenv()


class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions=AGENT_INSTRUCTION,
            tools=[help_request_tool],
        )


# Define the Agent
async def entrypoint(ctx: agents.JobContext):
    session = AgentSession(
        llm=google.realtime.RealtimeModel(
            voice=AGENT_VOICE,
            temperature=MODEL_TEMPERATURE,
        ),
    )

    await session.start(
        room=ctx.room,
        agent=Assistant(),
        room_input_options=RoomInputOptions(),
    )

    await session.generate_reply(instructions=SESSION_INSTRUCTION)


if __name__ == INIT_MAIN:
    delete_help_requests()
    delete_knowledge_base()

    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
