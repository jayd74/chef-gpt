import { NextRequest, NextResponse } from "next/server";
import { PrismaClient } from "@/generated/prisma";

const prisma = new PrismaClient();

export async function POST(request: NextRequest) {
  try {
    const { image, filename } = await request.json();

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
        filename: filename,
      }),
    });

    let analysis = null;
    if (response.ok) {
      analysis = await response.json();
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

    // Store the image and analysis in database
    const imageData = await prisma.foodImage.create({
      data: {
        filename,
        base64: image,
        analysis,
        // userId: session?.user?.id, // Add when authentication is implemented
      },
    });

    return NextResponse.json(analysis);
  } catch (error) {
    console.error("Error in recipe analysis:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}

export async function GET() {
  try {
    // Fetch all uploaded images from database
    const images = await prisma.foodImage.findMany({
      orderBy: {
        uploadedAt: "desc",
      },
      select: {
        id: true,
        filename: true,
        base64: true,
        uploadedAt: true,
        analysis: true,
      },
    });

    return NextResponse.json({ images });
  } catch (error) {
    console.error("Error fetching images:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}
