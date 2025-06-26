import json
import logging
import os
# import langchain_core
from datetime import datetime
from typing import Dict, Any, AsyncGenerator, List, Optional
from collections.abc import AsyncGenerator
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
# from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from openai import OpenAI
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from app.schemas import ChatState, ChatRequest, ChatResponse

# Configure logging
logger = logging.getLogger(__name__)

# System instructions for recipe management and generation
RECIPE_SYSTEM_PROMPT = """You are ChefGPT, a helpful and knowledgeable culinary assistant specialized in recipe management and generation. Your capabilities include:

**Recipe Generation:**
- Create detailed, step-by-step recipes from ingredients or dish names
- Suggest recipe variations and modifications
- Generate recipes based on dietary restrictions (vegetarian, vegan, gluten-free, etc.)
- Create recipes for specific occasions, cuisines, or skill levels
- Provide cooking tips and techniques

**Recipe Management:**
- Help users organize and categorize their recipes
- Suggest ingredient substitutions and alternatives
- Calculate nutritional information when possible
- Scale recipes up or down for different serving sizes
- Provide meal planning suggestions

**Culinary Expertise:**
- Explain cooking techniques and methods
- Provide food safety guidelines
- Suggest wine pairings and beverage recommendations
- Help with kitchen equipment and tools
- Offer troubleshooting advice for cooking problems

**Communication Style:**
- Be warm, encouraging, and enthusiastic about cooking
- Use clear, easy-to-follow language
- Provide helpful context and explanations
- Ask clarifying questions when needed
- Celebrate the user's culinary journey

Always prioritize food safety and provide accurate cooking information. When generating recipes, include:
- Prep time and cook time
- Serving size
- Complete ingredient list with measurements
- Step-by-step instructions
- Any special equipment needed
- Tips for best results

Politely decline to answer questions that are not related to cooking or recipe management.

Remember: Cooking should be fun and accessible to everyone, regardless of skill level!

"""

# Initialize LangChain components
def get_llm():
    """Get the language model"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable is required")

    client = OpenAI(api_key=api_key)
    return client

# Define the chat node
async def chat_node(state: ChatState) -> ChatState:
    """Process the chat message and generate a response"""
    client = get_llm()

    # Convert messages to OpenAI format
    messages = []
    
    # Always start with the system prompt for recipe management
    messages.append({"role": "system", "content": RECIPE_SYSTEM_PROMPT})
    
    for msg in state.messages:
        if msg["type"] == "human":
            messages.append({"role": "user", "content": msg["content"]})
        elif msg["type"] == "ai":
            messages.append({"role": "assistant", "content": msg["content"]})
        elif msg["type"] == "system":
            # Skip adding system messages from state since we have our hardcoded one
            continue

    # Generate response
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.7,
        stream=True
    )

    # Collect the full response
    full_content = ""
    for chunk in response:
        if chunk.choices[0].delta.content:
            full_content += chunk.choices[0].delta.content

    # Add AI response to state
    state.messages.append({
        "type": "ai",
        "content": full_content,
        "timestamp": datetime.now(),
    })

    return state

# Create the LangGraph workflow
def create_chat_graph():
    """Create the LangGraph workflow for chat"""
    workflow = StateGraph(ChatState)

    # Add nodes
    workflow.add_node("chat", chat_node)

    # Set entry point
    workflow.set_entry_point("chat")

    # Add edges
    workflow.add_edge("chat", END)

    # Compile the graph
    return workflow.compile(checkpointer=MemorySaver())

# Global graph instance
chat_graph = create_chat_graph()

async def chat_stream(request: ChatRequest) -> StreamingResponse:
    """Stream chat responses using LangGraph"""
    async def generate_stream() -> AsyncGenerator[str, None]:
        try:
            # Initialize state
            state = ChatState(
                messages=[{
                    "type": request.type,
                    "content": request.content,
                    "timestamp": datetime.now(),
                }],
                session_id=request.session_id,
                context=request.context
            )

            # Stream the initial message
            yield f"data: {json.dumps({'type': request.type, 'content': request.content, 'session_id': request.session_id})}\n\n"

            # Process with LangGraph
            async for event in chat_graph.astream_events(
                state,
                config={"configurable": {"thread_id": request.session_id}}
            ):
                if event["event"] == "on_chain_end" and event["name"] == "chat":
                    # Get the final response
                    event_data = event.get("data", {})
                    if isinstance(event_data, dict) and "output" in event_data:
                        final_state = event_data["output"]
                        messages = []

                        # Handle different types of final_state
                        if hasattr(final_state, 'messages'):
                            messages = final_state.messages
                        elif isinstance(final_state, dict):
                            messages = final_state.get('messages', [])

                        ai_message = next(
                            (msg for msg in messages if msg.get("type") == "ai"),
                            None
                        )

                        if ai_message:
                            # Stream the AI response
                            yield f"data: {json.dumps({'type': 'ai', 'content': ai_message.get('content', ''), 'session_id': request.session_id})}\n\n"

                    # Send end marker
                    yield f"data: {json.dumps({'type': 'end', 'content': '', 'session_id': request.session_id})}\n\n"
                    break

                elif event["event"] == "on_chat_model_stream":
                    # Stream individual tokens
                    event_data = event.get("data", {})
                    if isinstance(event_data, dict) and "chunk" in event_data:
                        chunk = event_data["chunk"]
                        if hasattr(chunk, 'content') and chunk.content:
                            yield f"data: {json.dumps({'type': 'token', 'content': chunk.content, 'session_id': request.session_id})}\n\n"

        except Exception as e:
            logger.error(f"Error in chat stream: {e}")
            yield f"data: {json.dumps({'type': 'error', 'content': str(e), 'session_id': request.session_id})}\n\n"

    return StreamingResponse(
        generate_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
        }
    )

# Non-streaming version for simple requests
async def chat_simple(request: ChatRequest) -> ChatResponse:
    """Simple non-streaming chat response"""
    try:
        # Initialize state
        state = ChatState(
            messages=[{
                "type": request.type,
                "content": request.content,
                "timestamp": datetime.now(),
            }],
            session_id=request.session_id,
            context=request.context
        )

        # Process with LangGraph
        result = await chat_graph.ainvoke(
            state,
            config={"configurable": {"thread_id": request.session_id}}
        )

        # Get AI response - handle both ChatState and dict types
        if isinstance(result, ChatState):
            messages = result.messages
        elif isinstance(result, dict) and 'messages' in result:
            messages = result['messages']
        else:
            messages = []

        ai_message = next(
            (msg for msg in messages if msg["type"] == "ai"),
            None
        )

        if ai_message:
            return ChatResponse(
                type="ai",
                content=ai_message["content"],
                session_id=request.session_id
            )
        else:
            return ChatResponse(
                type="error",
                content="No response generated",
                session_id=request.session_id
            )

    except Exception as e:
        logger.error(f"Error in chat: {e}")
        return ChatResponse(
            type="error",
            content=str(e),
            session_id=request.session_id
        )
