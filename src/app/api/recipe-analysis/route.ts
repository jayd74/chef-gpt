import { NextRequest, NextResponse } from "next/server";

export async function POST(request: NextRequest) {
  try {
    const { image } = await request.json();

    if (!image) {
      return NextResponse.json(
        { error: "Image data is required" },
        { status: 400 }
      );
    }

    // Call the ML backend
    const mlBackendUrl = process.env.ML_BACKEND_URL || "http://localhost:8000";

    const response = await fetch(`${mlBackendUrl}/recipe_analysis`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        image: image,
      }),
    });

    let analysis = null;
    if (response.ok) {
      analysis = JSON.parse(await response.json());
    } else {
      console.error("ML backend error:", response.status, response.statusText);
      // For now, return a mock analysis if ML backend is not available
      analysis = {
        food_name: "Unknown Food",
        confidence: 0.5,
        calories: 250,
        cooking_time: 30,
        ingredients: ["ingredient 1", "ingredient 2"],
        recipe: "This is a sample recipe based on the uploaded image.",
      };
    }

    return NextResponse.json(analysis);
  } catch (error) {
    console.error("Error in recipe analysis:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}
