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
    <div className="min-h-screen bg-gradient-to-br from-yellow-50 via-white to-yellow-100">
      {/* Header */}
      <header className="bg-gradient-to-r from-yellow-400 to-yellow-500 shadow-lg border-b-2 border-black/10 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-20">
            <div className="flex items-center space-x-4">
              <div className="p-2 bg-black/10 rounded-xl">
                <ChefHat className="h-8 w-8 text-black" />
              </div>
              <div>
                <h1 className="text-3xl font-bold text-black tracking-tight">
                  ChefGPT
                </h1>
                <p className="text-sm text-black/70 font-medium">
                  AI-Powered Recipe Analysis
                </p>
              </div>
            </div>
            <div className="flex items-center space-x-3 bg-white/20 backdrop-blur-sm rounded-full px-4 py-2">
              <Sparkles className="h-5 w-5 text-black" />
              <span className="text-sm text-black font-semibold">
                Powered by AI
              </span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
          {/* Upload Section */}
          <div className="space-y-8">
            <div className="bg-white/80 backdrop-blur-sm border border-black/10 rounded-2xl shadow-xl p-8 hover:shadow-2xl transition-all duration-300">
              <div className="flex items-center space-x-3 mb-6">
                <div className="p-2 bg-yellow-100 rounded-xl">
                  <Camera className="h-6 w-6 text-black" />
                </div>
                <div>
                  <h2 className="text-2xl font-bold text-black">
                    Upload Food Photo
                  </h2>
                  <p className="text-black/60 text-sm">
                    Get instant AI analysis
                  </p>
                </div>
              </div>
              <p className="text-black/80 mb-8 leading-relaxed">
                Take a photo or upload an image of your food to get AI-powered
                recipe analysis, nutritional information, and cooking
                suggestions.
              </p>
              <ImageUpload onImageUpload={handleImageUpload} />
            </div>

            {/* Quick Tips */}
            <div className="bg-gradient-to-br from-yellow-200 to-yellow-300 border border-black/10 rounded-2xl p-6 shadow-lg">
              <div className="flex items-center space-x-3 mb-4">
                <div className="p-2 bg-black/10 rounded-lg">
                  <span className="text-xl">💡</span>
                </div>
                <h3 className="font-bold text-black text-lg">
                  Tips for Best Results
                </h3>
              </div>
              <ul className="text-black/80 space-y-2 text-sm">
                <li className="flex items-center space-x-2">
                  <div className="w-1.5 h-1.5 bg-black rounded-full"></div>
                  <span>Ensure good lighting for clear photos</span>
                </li>
                <li className="flex items-center space-x-2">
                  <div className="w-1.5 h-1.5 bg-black rounded-full"></div>
                  <span>Include the entire dish in the frame</span>
                </li>
                <li className="flex items-center space-x-2">
                  <div className="w-1.5 h-1.5 bg-black rounded-full"></div>
                  <span>Avoid blurry or dark images</span>
                </li>
                <li className="flex items-center space-x-2">
                  <div className="w-1.5 h-1.5 bg-black rounded-full"></div>
                  <span>Supported formats: JPG, PNG, WebP</span>
                </li>
              </ul>
            </div>
          </div>

          {/* Display Section */}
          <div className="space-y-8">
            <div className="bg-white/80 backdrop-blur-sm border border-black/10 rounded-2xl shadow-xl p-8 hover:shadow-2xl transition-all duration-300">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h2 className="text-2xl font-bold text-black">
                    Your Food Photos
                  </h2>
                  <p className="text-black/60 text-sm">
                    Analysis results and insights
                  </p>
                </div>
                {uploadedImages.length > 0 && (
                  <Button
                    onClick={() =>
                      uploadedImages.forEach((img) =>
                        handleAnalyzeImage(img.id)
                      )
                    }
                    disabled={isAnalyzing}
                    className="bg-gradient-to-r from-black to-gray-800 text-yellow-400 hover:from-gray-800 hover:to-black border-2 border-black shadow-lg hover:shadow-xl transition-all duration-200 px-6 py-3 rounded-xl font-semibold"
                  >
                    {isAnalyzing ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-yellow-400 mr-2" />
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
                <div className="text-center py-16">
                  <div className="p-4 bg-yellow-100 rounded-full w-20 h-20 mx-auto mb-6 flex items-center justify-center">
                    <Upload className="h-10 w-10 text-black/60" />
                  </div>
                  <h3 className="text-lg font-semibold text-black mb-2">
                    No photos uploaded yet
                  </h3>
                  <p className="text-black/60">
                    Upload a food photo to get started with AI analysis
                  </p>
                </div>
              ) : (
                <div className="space-y-6">
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
