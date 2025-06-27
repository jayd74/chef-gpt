import { NextRequest, NextResponse } from "next/server";
import { API_ENDPOINTS } from "@/app/api/constants";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { flyer_url, banner } = body;

    if (!flyer_url && !banner) {
      return NextResponse.json(
        { error: "Either flyer_url or banner is required" },
        { status: 400 }
      );
    }

    // Call the deployed ML backend on Render
    const response = await fetch(API_ENDPOINTS.FLYER_DINNER, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(banner ? { banner } : { flyer_url }),
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
