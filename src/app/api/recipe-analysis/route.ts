import { NextRequest, NextResponse } from "next/server";
import { API_ENDPOINTS } from "@/app/api/constants";

export async function POST(request: NextRequest) {
  try {
    const { image } = await request.json();

    if (!image) {
      return NextResponse.json(
        { error: "Image data is required" },
        { status: 400 }
      );
    }

    // Call the deployed ML backend on Render
    const response = await fetch(API_ENDPOINTS.RECIPE_ANALYSIS, {
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
        dish_name: "Unknown Dish",
        description: "A delicious dish that was detected in your image.",
        tags: ["unknown", "detected"],
        recipe: "This is a sample recipe based on the uploaded image.",
        ingredients: ["ingredient 1", "ingredient 2", "ingredient 3"],
        nutrition_facts: {
          serving_size: "1 serving",
          calories: 250,
          protein: 15,
          carbohydrates: 30,
          fat: 10,
        },
        food_pairings: ["water", "side dish"],
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
