import { NextRequest, NextResponse } from "next/server";
import { API_ENDPOINTS } from "@/app/api/constants";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { type, content, session_id, context } = body;

    if (!type || !content) {
      return NextResponse.json(
        { error: "Type and content are required" },
        { status: 400 }
      );
    }

    // Call the deployed ML backend on Render
    const response = await fetch(API_ENDPOINTS.CHAT, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        type,
        content,
        session_id: session_id || "default",
        context: context || {},
      }),
    });

    if (!response.ok) {
      let errorText;
      try {
        errorText = await response.json();
      } catch {
        errorText = await response.text();
      }
      console.error("ML Backend Chat Error:", errorText);
      return NextResponse.json(
        { error: "Failed to process chat request" },
        { status: response.status }
      );
    }

    // Return the streaming response from the ML backend
    return new Response(response.body, {
      status: response.status,
      statusText: response.statusText,
      headers: {
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache",
        Connection: "keep-alive",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "*",
      },
    });
  } catch (error) {
    console.error("Chat API error:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}

export async function OPTIONS() {
  return new NextResponse(null, {
    status: 200,
    headers: {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type, Authorization",
    },
  });
}
