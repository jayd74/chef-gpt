"use client";

import { useState } from "react";
import { Upload, Camera, ChefHat, Sparkles } from "lucide-react";
import ImageUpload from "@/components/ImageUpload";
import ImageDisplay from "@/components/ImageDisplay";
import { Button } from "@/components/ui/button";

interface NutritionFacts {
  serving_size: string;
  calories: number;
  protein: number;
  carbohydrates: number;
  fat: number;
}

interface Analysis {
  dish_name?: string;
  description?: string;
  tags?: string[];
  recipe?: string;
  ingredients?: string[];
  nutrition_facts?: NutritionFacts;
  food_pairings?: string[];
}

interface FoodImage {
  id: string;
  base64: string;
  filename: string;
  uploadedAt: Date;
  analysis?: Analysis;
}

export default function Home() {
  const [uploadedImages, setUploadedImages] = useState<FoodImage[]>([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);

  const handleImageUpload = (base64: string, filename: string) => {
    const newImage: FoodImage = {
      id: Date.now().toString(),
      base64,
      filename,
      uploadedAt: new Date(),
    };
    setUploadedImages((prev) => [newImage, ...prev]);
  };

  const handleAnalyzeImage = async (imageId: string) => {
    setIsAnalyzing(true);
    try {
      const image = uploadedImages.find((img) => img.id === imageId);
      if (!image) return;

      const response = await fetch("/api/recipe-analysis", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          image: image.base64,
          filename: image.filename,
        }),
      });

      if (response.ok) {
        const analysis = await response.json();
        setUploadedImages((prev) =>
          prev.map((img) => (img.id === imageId ? { ...img, analysis } : img))
        );
      } else {
        console.error("Analysis failed");
      }
    } catch (error) {
      console.error("Error analyzing image:", error);
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 to-amber-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-3">
              <ChefHat className="h-8 w-8 text-orange-600" />
              <h1 className="text-2xl font-bold text-gray-900">ChefGPT</h1>
            </div>
            <div className="flex items-center space-x-2">
              <Sparkles className="h-5 w-5 text-orange-500" />
              <span className="text-sm text-gray-600">
                AI-Powered Recipe Analysis
              </span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Upload Section */}
          <div className="space-y-6">
            <div className="bg-white rounded-lg shadow-sm border p-6">
              <div className="flex items-center space-x-2 mb-4">
                <Camera className="h-5 w-5 text-orange-600" />
                <h2 className="text-xl font-semibold text-gray-900">
                  Upload Food Photo
                </h2>
              </div>
              <p className="text-gray-600 mb-6">
                Take a photo or upload an image of your food to get AI-powered
                recipe analysis, nutritional information, and cooking
                suggestions.
              </p>
              <ImageUpload onImageUpload={handleImageUpload} />
            </div>

            {/* Quick Tips */}
            <div className="bg-blue-50 rounded-lg p-4">
              <h3 className="font-medium text-blue-900 mb-2">
                💡 Tips for Best Results
              </h3>
              <ul className="text-sm text-blue-800 space-y-1">
                <li>• Ensure good lighting for clear photos</li>
                <li>• Include the entire dish in the frame</li>
                <li>• Avoid blurry or dark images</li>
                <li>• Supported formats: JPG, PNG, WebP</li>
              </ul>
            </div>
          </div>

          {/* Display Section */}
          <div className="space-y-6">
            <div className="bg-white rounded-lg shadow-sm border p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold text-gray-900">
                  Your Food Photos
                </h2>
                {uploadedImages.length > 0 && (
                  <Button
                    onClick={() =>
                      uploadedImages.forEach((img) =>
                        handleAnalyzeImage(img.id)
                      )
                    }
                    disabled={isAnalyzing}
                    className="bg-orange-600 hover:bg-orange-700"
                  >
                    {isAnalyzing ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2" />
                        Analyzing...
                      </>
                    ) : (
                      <>
                        <Sparkles className="h-4 w-4 mr-2" />
                        Analyze All
                      </>
                    )}
                  </Button>
                )}
              </div>

              {uploadedImages.length === 0 ? (
                <div className="text-center py-12">
                  <Upload className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <p className="text-gray-500">No photos uploaded yet</p>
                  <p className="text-sm text-gray-400">
                    Upload a food photo to get started
                  </p>
                </div>
              ) : (
                <div className="space-y-4">
                  {uploadedImages.map((image) => (
                    <ImageDisplay
                      key={image.id}
                      image={image}
                      onAnalyze={() => handleAnalyzeImage(image.id)}
                      isAnalyzing={isAnalyzing}
                    />
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
