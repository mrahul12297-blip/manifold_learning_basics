# logging module in python

import logging
import json
from datetime import datetime
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
import uuid

load_dotenv()

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

logger = logging.getLogger("llm_agent")

llm_openai = ChatOpenAI(model="gpt-5.4-mini")
conversation = [SystemMessage(content="You are a helpful assistant.")]

# key things need to log

def log_invoke(user_message: str, session_id: str = "demo_session"):
    start_time = datetime.now()

    conversation.append(HumanMessage(content=user_message))

    logger.info(json.dumps({
        "event": "LLM_call_started",
        "session_id": session_id,
        "start_time": start_time.isoformat(),
        "user_message": user_message,
        "conversation": conversation,
        "model": "gpt-5.4-mini",
    }))

    try:
        response = llm_openai.invoke(conversation)

        latency = (datetime.now() - start_time).total_seconds() * 1000

        conversation.append(AIMessage(content=response.content))

        logger.info(json.dumps({
            "event": "LLM_call_completed",
            "session_id": session_id,
            "start_time": start_time.isoformat(),
            "latency": latency,
            "response": response.content,
            "conversation": conversation,
            "output_tokens": response.response_metadata.get("completion_tokens"),
            "input_tokens": response.response_metadata.get("prompt_tokens"),
        }))

        return response.content

    except Exception as e:
        latency = (datetime.now() - start_time).total_seconds() * 1000

        logger.error(json.dumps({
            "event": "LLM_call_failed",
            "session_id": session_id,
            "start_time": start_time.isoformat(),
            "error": str(e),
        }))

        raise e


session_id = str(uuid.uuid4())

result = log_invoke(
    "What is the capital of France?",
    session_id=session_id
)

print(result)