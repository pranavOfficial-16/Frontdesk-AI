from livekit import agents
from dotenv import load_dotenv
from tools import help_request
from livekit.plugins import google, noise_cancellation
from prompts import AGENT_INSTRUCTION, SESSION_INSTRUCTION
from livekit.agents import AgentSession, Agent, RoomInputOptions
from firebase import delete_help_requests, delete_knowledge_base


load_dotenv()


class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions=AGENT_INSTRUCTION,
            tools=[help_request],
        )


async def entrypoint(ctx: agents.JobContext):
    session = AgentSession(
        stt="assemblyai/universal-streaming:en",
        llm=google.beta.realtime.RealtimeModel(
            voice="Charon",
            temperature=0.8,
        ),
    )

    await session.start(
        room=ctx.room,
        agent=Assistant(),
        room_input_options=RoomInputOptions(
            noise_cancellation=noise_cancellation.BVC()
        ),
    )

    await session.generate_reply(instructions=SESSION_INSTRUCTION)


if __name__ == "__main__":
    # DELETE collections in firebase at start
    delete_help_requests()
    delete_knowledge_base()

    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
