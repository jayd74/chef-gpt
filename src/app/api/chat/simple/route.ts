import { NextRequest, NextResponse } from "next/server";

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

    // Call the deployed ML backend using environment variable
    const mlBackendUrl = process.env.ML_BACKEND_URL || "http://localhost:8000";
    const response = await fetch(`${mlBackendUrl}/chat/simple`, {
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
      const errorText = await response.text();
      console.error("ML Backend Chat Error:", errorText);
      return NextResponse.json(
        { error: "Failed to process chat request" },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error("Chat API error:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}
