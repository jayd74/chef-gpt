"use client";

import { useState } from "react";
import { ChefHat, Loader2, Link, X, Maximize2 } from "lucide-react";
import ReactMarkdown from "react-markdown";

interface FlyerAnalysis {
  dish_name?: string;
  description?: string;
  tags?: string[];
  recipe?: string;
  ingredients?: string[];
  cost?: number;
  nutrition_facts?: {
    serving_size: string;
    calories: number;
    protein: number;
    carbohydrates: number;
    fat: number;
  };
  flyer_url?: string;
}

interface FlyerDinnerUploadProps {
  onAnalysisComplete?: (analysis: FlyerAnalysis) => void;
}

export default function FlyerDinnerUpload({
  onAnalysisComplete,
}: FlyerDinnerUploadProps) {
  const [flyerUrl, setFlyerUrl] = useState<string>("");
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysis, setAnalysis] = useState<FlyerAnalysis | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showModal, setShowModal] = useState(false);

  const analyzeFlyer = async () => {
    if (!flyerUrl.trim()) {
      setError("Please enter a flyer URL");
      return;
    }

    setIsAnalyzing(true);
    setError(null);

    try {
      const response = await fetch("/api/flyer-dinner", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          flyer_url: flyerUrl.trim(),
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to analyze flyer");
      }

      const data = JSON.parse(await response.json());

      setAnalysis(data);
      onAnalysisComplete?.(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleIngredientClick = (ingredient: string) => {
    const encodedSearch = encodeURIComponent(ingredient);
    const url = `https://www.nofrills.ca/search?search-bar=${encodedSearch}`;
    window.open(url, "_blank");
  };

  const openModal = () => setShowModal(true);
  const closeModal = () => setShowModal(false);

  return (
    <div className="w-full max-w-4xl mx-auto">
      {/* URL Input Section */}
      <div className="bg-white rounded-3xl shadow-lg p-6 mb-6 border border-black/10">
        <h2 className="text-2xl font-bold text-black mb-4 flex items-center gap-2">
          <ChefHat className="w-6 h-6" />
          Flyer Dinner Planner
        </h2>
        <p className="text-black/70 mb-6">
          Enter a grocery flyer URL and get recipe suggestions based on the
          ingredients on sale!
        </p>

        {/* URL Input */}
        <div className="space-y-4">
          <div>
            <label
              htmlFor="flyer-url"
              className="block text-sm font-medium text-black mb-2"
            >
              Flyer URL
            </label>
            <div className="flex gap-3">
              <input
                id="flyer-url"
                type="url"
                value={flyerUrl}
                onChange={(e) => setFlyerUrl(e.target.value)}
                placeholder="https://example.com/flyer-image.jpg"
                className="flex-1 px-4 py-3 border border-black/20 rounded-2xl focus:outline-none focus:ring-2 focus:ring-yellow-400 focus:border-transparent text-black placeholder-black/40"
              />
              <button
                onClick={analyzeFlyer}
                disabled={isAnalyzing || !flyerUrl.trim()}
                className="bg-black text-yellow-400 px-6 py-3 rounded-2xl hover:bg-gray-800 transition-colors font-semibold disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 whitespace-nowrap"
              >
                {isAnalyzing ? (
                  <>
                    <Loader2 className="w-5 h-5 animate-spin" />
                    Analyzing...
                  </>
                ) : (
                  <>
                    <Link className="w-5 h-5" />
                    Analyze
                  </>
                )}
              </button>
            </div>
          </div>
        </div>

        {error && (
          <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-2xl text-red-700">
            {error}
          </div>
        )}
      </div>

      {/* Thumbnail Preview Section */}
      {flyerUrl && !isAnalyzing && (
        <div className="bg-white rounded-3xl shadow-lg p-6 mb-6 border border-black/10">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-xl font-bold text-black">Flyer Preview</h3>
            <button
              onClick={openModal}
              className="p-2 bg-yellow-100 rounded-full hover:bg-yellow-200 transition-colors"
              title="View larger image"
            >
              <Maximize2 className="w-4 h-4 text-black" />
            </button>
          </div>
          <div className="relative">
            <div
              className="w-48 h-32 rounded-2xl overflow-hidden shadow-md cursor-pointer hover:shadow-lg transition-shadow"
              onClick={openModal}
            >
              <img
                src={flyerUrl}
                alt="Flyer preview"
                className="w-full h-full object-cover"
                onError={(e) => {
                  e.currentTarget.style.display = "none";
                  e.currentTarget.nextElementSibling?.classList.remove(
                    "hidden"
                  );
                }}
              />
              <div className="hidden w-full h-full bg-gray-100 flex items-center justify-center">
                <Link className="w-8 h-8 text-gray-400" />
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Modal for Large Flyer View */}
      {showModal && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-3xl max-w-4xl max-h-[90vh] overflow-hidden relative">
            <div className="flex items-center justify-between p-6 border-b border-black/10">
              <h3 className="text-xl font-bold text-black">Flyer Image</h3>
              <button
                onClick={closeModal}
                className="p-2 bg-gray-100 rounded-full hover:bg-gray-200 transition-colors"
              >
                <X className="w-5 h-5 text-black" />
              </button>
            </div>
            <div className="p-6 overflow-auto max-h-[calc(90vh-120px)]">
              <img
                src={flyerUrl}
                alt="Flyer full view"
                className="w-full h-auto rounded-2xl shadow-lg"
                onError={(e) => {
                  e.currentTarget.style.display = "none";
                  e.currentTarget.nextElementSibling?.classList.remove(
                    "hidden"
                  );
                }}
              />
              <div className="hidden bg-gray-100 rounded-2xl p-8 text-center">
                <Link className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500">Unable to load flyer image</p>
                <p className="text-gray-400 text-sm mt-2">
                  The URL may be invalid or the image may not be accessible
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Analysis Results */}
      {analysis && (
        <div className="bg-white rounded-3xl shadow-lg p-6 border border-black/10">
          <h3 className="text-xl font-bold text-black mb-4">Recipe Analysis</h3>

          {/* Dish Name and Description */}
          <div className="mb-6">
            <h4 className="text-2xl font-bold text-black mb-3">
              {analysis.dish_name || "Recipe"}
            </h4>
            {analysis.description && (
              <p className="text-black/70 leading-relaxed mb-4">
                {analysis.description}
              </p>
            )}
          </div>

          {/* Tags */}
          {analysis.tags && analysis.tags.length > 0 && (
            <div className="mb-6">
              <h5 className="font-semibold text-black mb-3">Tags</h5>
              <div className="flex flex-wrap gap-2">
                {analysis.tags.map((tag, index) => (
                  <span
                    key={index}
                    className="bg-yellow-100 text-black px-3 py-1 rounded-full text-sm border border-yellow-300"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Cost */}
          {analysis.cost && (
            <div className="mb-6">
              <h5 className="font-semibold text-black mb-2">Estimated Cost</h5>
              <p className="text-2xl font-bold text-green-600">
                ${analysis.cost}
              </p>
            </div>
          )}

          {/* Nutrition Facts */}
          {analysis.nutrition_facts && (
            <div className="mb-6">
              <h5 className="font-semibold text-black mb-3">Nutrition Facts</h5>
              <div className="bg-yellow-50/50 rounded-2xl p-4 border border-yellow-200">
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className="text-center">
                    <div className="text-lg font-bold text-black">
                      {analysis.nutrition_facts.calories}
                    </div>
                    <div className="text-sm text-black/60">Calories</div>
                  </div>
                  <div className="text-center">
                    <div className="text-lg font-bold text-black">
                      {analysis.nutrition_facts.protein}g
                    </div>
                    <div className="text-sm text-black/60">Protein</div>
                  </div>
                  <div className="text-center">
                    <div className="text-lg font-bold text-black">
                      {analysis.nutrition_facts.carbohydrates}g
                    </div>
                    <div className="text-sm text-black/60">Carbs</div>
                  </div>
                  <div className="text-center">
                    <div className="text-lg font-bold text-black">
                      {analysis.nutrition_facts.fat}g
                    </div>
                    <div className="text-sm text-black/60">Fat</div>
                  </div>
                </div>
                <div className="text-center mt-3 text-sm text-black/60">
                  Serving: {analysis.nutrition_facts.serving_size}
                </div>
              </div>
            </div>
          )}

          {/* Ingredients */}
          {analysis.ingredients && analysis.ingredients.length > 0 && (
            <div className="mb-6">
              <h5 className="font-semibold text-black mb-3">Ingredients</h5>
              <div className="flex flex-wrap gap-2">
                {analysis.ingredients.map((ingredient, index) => (
                  <button
                    key={index}
                    onClick={() => handleIngredientClick(ingredient)}
                    className="bg-yellow-100 text-black px-3 py-1 rounded-full text-sm hover:bg-yellow-200 transition-colors border border-yellow-300"
                  >
                    {ingredient}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Recipe Instructions */}
          {analysis.recipe && (
            <div>
              <h5 className="font-semibold text-black mb-3">
                Recipe Instructions
              </h5>
              <div className="bg-yellow-50/50 rounded-2xl p-4 border border-yellow-200">
                <ReactMarkdown>{analysis.recipe}</ReactMarkdown>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
