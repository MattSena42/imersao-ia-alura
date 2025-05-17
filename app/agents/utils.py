from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types as genai_types

def call_agent(agent: Agent, message_text: str, app_name: str = "gemini_job_search") -> str:
    """
    Envia uma mensagem para um agente e retorna a resposta final como string.
    """
    session_service = InMemorySessionService()
    session = session_service.create_session(app_name=app_name, user_id="user_default", session_id="session_default")
    runner = Runner(agent=agent, app_name=app_name, session_service=session_service)

    content = genai_types.Content(role="user", parts=[genai_types.Part(text=message_text)])

    final_response_text = ""
    for event in runner.run(user_id="user_default", session_id="session_default", new_message=content):
        if event.is_final_response():
            for part in event.content.parts:
                if part.text is not None:
                    final_response_text += part.text
                    if not final_response_text.endswith("\n"):
                         final_response_text += " "
    return final_response_text.strip()