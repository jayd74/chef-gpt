import { NextRequest, NextResponse } from "next/server";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { flyer_url } = body;

    if (!flyer_url) {
      return NextResponse.json(
        { error: "Flyer URL is required" },
        { status: 400 }
      );
    }

    // Call the ML backend
    const mlBackendUrl = process.env.ML_BACKEND_URL || "http://localhost:8000";
    const response = await fetch(`${mlBackendUrl}/flyer_dinner`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        flyer_url: flyer_url,
      }),
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error("ML Backend Error:", errorText);
      return NextResponse.json(
        { error: "Failed to analyze flyer" },
        { status: response.status }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error("Flyer dinner analysis error:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}
