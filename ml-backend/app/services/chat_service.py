import json
import logging
import os
from typing import Dict, Any, AsyncGenerator, List, Optional
from collections.abc import AsyncGenerator
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from openai import OpenAI
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

# Configure logging
logger = logging.getLogger(__name__)

# Pydantic models for request/response
class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"
    context: Dict[str, Any] = {}

class ChatResponse(BaseModel):
    type: str
    content: str
    session_id: str

# Define the state structure
class ChatState(BaseModel):
    messages: List[Dict[str, Any]]
    session_id: str
    context: Dict[str, Any] = {}

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
    for msg in state.messages:
        if msg["type"] == "human":
            messages.append({"role": "user", "content": msg["content"]})
        elif msg["type"] == "ai":
            messages.append({"role": "assistant", "content": msg["content"]})
        elif msg["type"] == "system":
            messages.append({"role": "system", "content": msg["content"]})
    
    # Add system context if available
    if state.context.get("system_prompt"):
        messages.insert(0, {"role": "system", "content": state.context["system_prompt"]})
    
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
        "timestamp": "2024-01-01T00:00:00Z"  # In real app, use datetime.now()
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
                    "type": "human",
                    "content": request.message,
                    "timestamp": "2024-01-01T00:00:00Z"
                }],
                session_id=request.session_id,
                context=request.context
            )
            
            # Stream the initial human message
            yield f"data: {json.dumps({'type': 'human', 'content': request.message, 'session_id': request.session_id})}\n\n"
            
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
                        if hasattr(final_state, 'messages'):
                            ai_message = next(
                                (msg for msg in final_state.messages if msg["type"] == "ai"),
                                None
                            )
                            
                            if ai_message:
                                # Stream the AI response
                                yield f"data: {json.dumps({'type': 'ai', 'content': ai_message['content'], 'session_id': request.session_id})}\n\n"
                    
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
                "type": "human",
                "content": request.message,
                "timestamp": "2024-01-01T00:00:00Z"
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
        if hasattr(result, 'messages'):
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
