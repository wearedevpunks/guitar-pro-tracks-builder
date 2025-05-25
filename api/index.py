import json
import os
from contextlib import asynccontextmanager
from typing import List
from openai.types.chat.chat_completion_message_param import ChatCompletionMessageParam
from pydantic import BaseModel
from dotenv import load_dotenv
from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse, RedirectResponse
from openai import OpenAI
from api.utils.prompt import ClientMessage, convert_to_openai_messages
from api.utils.tools import get_current_weather
from api.settings.app_settings import settings
from api.routes import songs_router
from api.infrastructure.logging import get_logger


load_dotenv(".env.local")
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for startup and shutdown events."""
    # Startup
    try:
        # Get the OpenAPI schema
        openapi_schema = app.openapi()
        
        # Create output directory if it doesn't exist
        output_dir = "api_docs"
        os.makedirs(output_dir, exist_ok=True)
        
        # Write schema to file
        schema_file = os.path.join(output_dir, "openapi.json")
        with open(schema_file, "w", encoding="utf-8") as f:
            json.dump(openapi_schema, f, indent=2, ensure_ascii=False)
        
        logger.info(f"OpenAPI schema dumped to {schema_file}")
        
    except Exception as e:
        logger.error(f"Failed to dump OpenAPI schema: {e}")
    
    yield
    
    # Shutdown (if needed)
    logger.info("Application shutting down")


app = FastAPI(
    title="Tabbo API",
    description="API for building and managing Guitar Pro tracks with AI assistance",
    version="1.0.0",
    docs_url="/swagger",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Include routers
app.include_router(songs_router)

client = OpenAI(
    api_key=settings.openai_api_key,
)


class Request(BaseModel):
    """Chat request containing conversation messages."""
    messages: List[ClientMessage]
    
    class Config:
        schema_extra = {
            "example": {
                "messages": [
                    {
                        "role": "user",
                        "content": "What's the weather like in New York?"
                    }
                ]
            }
        }


available_tools = {
    "get_current_weather": get_current_weather,
}

# Tool configuration for OpenAI API
TOOLS_CONFIG = [{
    "type": "function",
    "function": {
        "name": "get_current_weather",
        "description": "Get the current weather at a location",
        "parameters": {
            "type": "object",
            "properties": {
                "latitude": {
                    "type": "number",
                    "description": "The latitude of the location",
                },
                "longitude": {
                    "type": "number",
                    "description": "The longitude of the location",
                },
            },
            "required": ["latitude", "longitude"],
        },
    },
}]


@app.get("/", include_in_schema=False)
async def root():
    """Redirect to Swagger documentation."""
    return RedirectResponse(url="/swagger")

def do_stream(messages: List[ChatCompletionMessageParam]):
    stream = client.chat.completions.create(
        messages=messages,
        model=settings.openai_model,
        stream=True,
        tools=TOOLS_CONFIG
    )
    return stream

def stream_text(messages: List[ChatCompletionMessageParam], protocol: str = 'data'):
    draft_tool_calls = []
    draft_tool_calls_index = -1

    stream = client.chat.completions.create(
        messages=messages,
        model=settings.openai_model,
        stream=True,
        tools=TOOLS_CONFIG
    )

    for chunk in stream:
        for choice in chunk.choices:
            if choice.finish_reason == "stop":
                continue

            elif choice.finish_reason == "tool_calls":
                for tool_call in draft_tool_calls:
                    yield '9:{{"toolCallId":"{id}","toolName":"{name}","args":{args}}}\n'.format(
                        id=tool_call["id"],
                        name=tool_call["name"],
                        args=tool_call["arguments"])

                for tool_call in draft_tool_calls:
                    tool_result = available_tools[tool_call["name"]](
                        **json.loads(tool_call["arguments"]))

                    yield 'a:{{"toolCallId":"{id}","toolName":"{name}","args":{args},"result":{result}}}\n'.format(
                        id=tool_call["id"],
                        name=tool_call["name"],
                        args=tool_call["arguments"],
                        result=json.dumps(tool_result))

            elif choice.delta.tool_calls:
                for tool_call in choice.delta.tool_calls:
                    call_id = tool_call.id
                    name = tool_call.function.name
                    arguments = tool_call.function.arguments

                    if call_id is not None:
                        draft_tool_calls_index += 1
                        draft_tool_calls.append(
                            {"id": call_id, "name": name, "arguments": ""})

                    else:
                        draft_tool_calls[draft_tool_calls_index]["arguments"] += arguments

            else:
                yield '0:{text}\n'.format(text=json.dumps(choice.delta.content))

        if not chunk.choices:
            usage = chunk.usage
            prompt_tokens = usage.prompt_tokens
            completion_tokens = usage.completion_tokens

            yield 'e:{{"finishReason":"{reason}","usage":{{"promptTokens":{prompt},"completionTokens":{completion}}},"isContinued":false}}\n'.format(
                reason="tool-calls" if draft_tool_calls else "stop",
                prompt=prompt_tokens,
                completion=completion_tokens
            )




@app.post(
    "/api/chat",
    summary="Chat with AI Assistant",
    description="Stream chat responses from OpenAI with tool calling support for weather information",
    tags=["Chat"]
)
async def handle_chat_data(
    request: Request, 
    protocol: str = Query('data', description="Response protocol format")
):
    """
    Chat with the AI assistant that can provide weather information.
    
    The endpoint returns a streaming response with the AI's messages and tool calls.
    """
    messages = request.messages
    openai_messages = convert_to_openai_messages(messages)

    response = StreamingResponse(
        stream_text(openai_messages, protocol),
        media_type="text/plain"
    )
    response.headers['x-vercel-ai-data-stream'] = 'v1'
    return response


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.host, port=settings.port, log_level=settings.log_level.lower())
