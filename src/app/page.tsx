"use client";

import { useState } from "react";
import { ChefHat, Camera, Sparkles, Upload, Hamburger } from "lucide-react";
import { Button } from "@/components/ui/button";
import ImageUpload from "@/components/ImageUpload";
import ImageDisplay from "@/components/ImageDisplay";

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
  data: string;
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
      data: base64,
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
          image: image.data,
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
      <header className="bg-white shadow-sm border-b border-black/10 sticky top-0 z-40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-yellow-100 rounded-full">
                <ChefHat className="h-6 w-6 text-black" />
              </div>
              <h1 className="text-2xl font-bold text-black">ChefGPT</h1>
            </div>
            <div className="flex items-center space-x-4">
              <div className="hidden md:flex items-center space-x-2 bg-yellow-50 rounded-full px-3 py-1">
                <Sparkles className="h-4 w-4 text-black" />
                <span className="text-sm text-black font-medium">
                  AI-Powered
                </span>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-4xl md:text-5xl font-bold text-black mb-6">
            Discover Amazing Recipes with AI
          </h2>
          <p className="text-xl text-black/70 mb-8 leading-relaxed">
            Upload a photo of any dish and get instant recipe analysis,
            nutritional insights, and cooking inspiration.
          </p>
        </div>
      </section>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-12">
        {/* Upload Section */}
        <div className="mb-12">
          <div className="bg-white rounded-3xl shadow-lg border border-black/5 p-8 max-w-2xl mx-auto">
            <div className="text-center mb-8">
              <div className="p-4 bg-yellow-100 rounded-full w-16 h-16 mx-auto mb-4 flex items-center justify-center">
                <Hamburger className="h-8 w-8 text-black" />
              </div>
              <h2 className="text-2xl font-bold text-black mb-2">
                Upload Your Food Photo
              </h2>
              <p className="text-black/60">
                Get instant AI-powered recipe analysis and cooking tips
              </p>
            </div>
            <ImageUpload onImageUpload={handleImageUpload} />
          </div>
        </div>

        {/* Food Photos Grid */}
        {uploadedImages.length > 0 && (
          <div className="mb-8">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-2xl font-bold text-black">
                Your Food Collection
              </h3>
              <Button
                onClick={() =>
                  uploadedImages.forEach((img) => handleAnalyzeImage(img.id))
                }
                disabled={isAnalyzing}
                className="bg-black text-yellow-400 hover:bg-gray-800 px-6 py-2 rounded-full font-semibold transition-colors shadow-lg"
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
            </div>
          </div>
        )}

        {/* Pinterest-style Grid */}
        <div className="columns-1 md:columns-2 lg:columns-3 gap-6 space-y-6">
          {uploadedImages.length === 0 ? (
            <div className="col-span-full text-center py-16">
              <div className="p-6 bg-yellow-100 rounded-full w-24 h-24 mx-auto mb-6 flex items-center justify-center">
                <Upload className="h-12 w-12 text-black/60" />
              </div>
              <h3 className="text-xl font-semibold text-black mb-2">
                Start Your Food Journey
              </h3>
              <p className="text-black/60 max-w-md mx-auto">
                Upload your first food photo to discover recipes, nutrition
                facts, and cooking inspiration
              </p>
            </div>
          ) : (
            uploadedImages.map((image) => (
              <div key={image.id} className="break-inside-avoid mb-6">
                <ImageDisplay
                  image={image}
                  onAnalyze={() => handleAnalyzeImage(image.id)}
                  isAnalyzing={isAnalyzing}
                />
              </div>
            ))
          )}
        </div>

        {/* Tips Section */}
        <div className="mt-16">
          <div className="bg-gradient-to-br from-yellow-100 to-yellow-200 rounded-3xl p-8 shadow-lg">
            <div className="text-center mb-8">
              <div className="p-3 bg-black/10 rounded-full w-12 h-12 mx-auto mb-4 flex items-center justify-center">
                <span className="text-2xl">💡</span>
              </div>
              <h3 className="text-2xl font-bold text-black mb-2">
                Tips for Best Results
              </h3>
              <p className="text-black/70">
                Get the most out of your AI recipe analysis
              </p>
            </div>
            <div className="grid md:grid-cols-2 gap-6">
              <div className="bg-white/60 rounded-2xl p-6">
                <h4 className="font-semibold text-black mb-3">
                  📸 Perfect Photos
                </h4>
                <ul className="text-black/70 space-y-2 text-sm">
                  <li>• Ensure good lighting for clear photos</li>
                  <li>• Include the entire dish in the frame</li>
                  <li>• Avoid blurry or dark images</li>
                </ul>
              </div>
              <div className="bg-white/60 rounded-2xl p-6">
                <h4 className="font-semibold text-black mb-3">
                  🎯 Best Practices
                </h4>
                <ul className="text-black/70 space-y-2 text-sm">
                  <li>• Supported formats: JPG, PNG, WebP</li>
                  <li>• Maximum file size: 10MB</li>
                  <li>• Take photos from different angles</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
