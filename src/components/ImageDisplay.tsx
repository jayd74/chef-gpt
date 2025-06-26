"use client";

import { ChefHat } from "lucide-react";

interface NutritionFacts {
  serving_size: string;
  calories: number;
  protein: number;
  carbohydrates: number;
  fat: number;
}

interface RecipeAnalysis {
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
  analysis?: RecipeAnalysis;
}

interface ImageDisplayProps {
  image: FoodImage;
  onAnalyze: () => void;
  isAnalyzing: boolean;
}

export default function ImageDisplay({
  image,
  onAnalyze,
  isAnalyzing,
}: ImageDisplayProps) {
  const handleIngredientClick = (ingredient: string) => {
    const encodedSearch = encodeURIComponent(ingredient);
    const url = `https://www.nofrills.ca/search?search-bar=${encodedSearch}`;
    window.open(url, "_blank");
  };

  const handleBuyAllIngredients = () => {
    if (image.analysis?.ingredients) {
      const allIngredients = image.analysis.ingredients.join(" ");
      const encodedSearch = encodeURIComponent(allIngredients);
      const url = `https://www.nofrills.ca/search?search-bar=${encodedSearch}`;
      window.open(url, "_blank");
    }
  };

  return (
    <div className="bg-white/90 backdrop-blur-sm border border-black/10 rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 p-6">
      {/* Image */}
      <div className="relative mb-6">
        <img
          src={image.data}
          alt="Uploaded food"
          className="w-full h-48 object-cover rounded-xl shadow-md"
        />
        <div className="absolute top-3 right-3">
          <button
            onClick={() => onAnalyze()}
            disabled={isAnalyzing}
            className="bg-gradient-to-r from-black to-gray-800 text-yellow-400 hover:from-gray-800 hover:to-black disabled:bg-gray-400 disabled:text-gray-600 px-4 py-2 rounded-lg shadow-lg hover:shadow-xl transition-all duration-200 font-semibold text-sm flex items-center space-x-2"
          >
            {isAnalyzing ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-yellow-400" />
                <span>Analyzing...</span>
              </>
            ) : (
              <>
                <ChefHat className="h-4 w-4" />
                <span>Analyze</span>
              </>
            )}
          </button>
        </div>
      </div>

      {/* Analysis Results */}
      {image.analysis && (
        <div className="space-y-6">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-yellow-100 rounded-lg">
              <ChefHat className="h-5 w-5 text-black" />
            </div>
            <div>
              <span className="text-sm font-semibold text-black">
                Analysis Complete
              </span>
              <p className="text-xs text-black/60">AI-powered insights</p>
            </div>
          </div>

          <div className="bg-gradient-to-br from-yellow-50 to-white border border-black/10 rounded-xl p-6 shadow-sm">
            {/* Dish Name and Description */}
            <div className="mb-6">
              <h4 className="font-bold text-black text-xl mb-2">
                {image.analysis.dish_name || "Unknown Dish"}
              </h4>
              {image.analysis.description && (
                <p className="text-black/70 leading-relaxed">
                  {image.analysis.description}
                </p>
              )}
            </div>

            {/* Tags */}
            {image.analysis.tags && image.analysis.tags.length > 0 && (
              <div className="mb-6">
                <span className="text-black font-semibold text-sm mb-3 block">
                  Tags:
                </span>
                <div className="flex flex-wrap gap-2">
                  {image.analysis.tags.map((tag: string, index: number) => (
                    <span
                      key={index}
                      className="bg-gradient-to-r from-yellow-200 to-yellow-300 text-black text-xs px-3 py-1.5 rounded-full border border-black/20 font-medium shadow-sm"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Nutrition Facts */}
            {image.analysis.nutrition_facts && (
              <div className="mb-6">
                <span className="text-black font-semibold text-sm mb-3 block">
                  Nutrition Facts:
                </span>
                <div className="grid grid-cols-2 gap-4 bg-white/50 rounded-lg p-4">
                  <div className="text-center">
                    <span className="text-black/60 text-xs block">Serving</span>
                    <p className="font-bold text-black">
                      {image.analysis.nutrition_facts.serving_size}
                    </p>
                  </div>
                  <div className="text-center">
                    <span className="text-black/60 text-xs block">
                      Calories
                    </span>
                    <p className="font-bold text-black">
                      {image.analysis.nutrition_facts.calories} kcal
                    </p>
                  </div>
                  <div className="text-center">
                    <span className="text-black/60 text-xs block">Protein</span>
                    <p className="font-bold text-black">
                      {image.analysis.nutrition_facts.protein}g
                    </p>
                  </div>
                  <div className="text-center">
                    <span className="text-black/60 text-xs block">Carbs</span>
                    <p className="font-bold text-black">
                      {image.analysis.nutrition_facts.carbohydrates}g
                    </p>
                  </div>
                  <div className="text-center col-span-2">
                    <span className="text-black/60 text-xs block">Fat</span>
                    <p className="font-bold text-black">
                      {image.analysis.nutrition_facts.fat}g
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* Ingredients */}
            {image.analysis.ingredients &&
              image.analysis.ingredients.length > 0 && (
                <div className="mb-6">
                  <span className="text-black font-semibold text-sm mb-3 block">
                    Ingredients:
                  </span>
                  <div className="flex flex-wrap gap-2 mb-4">
                    {image.analysis.ingredients.map(
                      (ingredient: string, index: number) => (
                        <button
                          key={index}
                          onClick={() => handleIngredientClick(ingredient)}
                          className="bg-white/80 text-black text-xs px-3 py-2 rounded-lg hover:bg-yellow-200 hover:shadow-md border border-black/10 transition-all duration-200 flex items-center gap-2 cursor-pointer font-medium"
                          title={`Buy ${ingredient} at No Frills`}
                        >
                          <span>{ingredient}</span>
                          <svg
                            className="w-3 h-3"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                          >
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth={2}
                              d="M3 3h2l.4 2M7 13h10l4-8H5.4m0 0L7 13m0 0l-2.5 5M7 13l2.5 5m6-5v6a2 2 0 01-2 2H9a2 2 0 01-2-2v-6m6 0V9a2 2 0 00-2-2H9a2 2 0 00-2 2v4.01"
                            />
                          </svg>
                        </button>
                      )
                    )}
                  </div>
                  <div className="mb-3">
                    <button
                      onClick={handleBuyAllIngredients}
                      className="bg-gradient-to-r from-black to-gray-800 text-yellow-400 text-sm px-4 py-2 rounded-lg flex items-center gap-2 transition-all duration-200 border-2 border-black hover:from-gray-800 hover:to-black shadow-lg hover:shadow-xl font-semibold"
                      title="Buy all ingredients at No Frills"
                    >
                      <svg
                        className="w-4 h-4"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M3 3h2l.4 2M7 13h10l4-8H5.4m0 0L7 13m0 0l-2.5 5M7 13l2.5 5m6-5v6a2 2 0 01-2 2H9a2 2 0 01-2-2v-6m6 0V9a2 2 0 00-2-2H9a2 2 0 00-2 2v4.01"
                        />
                      </svg>
                      Buy All Ingredients
                    </button>
                  </div>
                  <p className="text-xs text-black/60">
                    Click ingredients to buy at No Frills
                  </p>
                </div>
              )}

            {/* Food Pairings */}
            {image.analysis.food_pairings &&
              image.analysis.food_pairings.length > 0 && (
                <div className="mb-6">
                  <span className="text-black font-semibold text-sm mb-3 block">
                    Goes well with:
                  </span>
                  <div className="flex flex-wrap gap-2 mb-4">
                    {image.analysis.food_pairings.map(
                      (pairing: string, index: number) => (
                        <button
                          key={index}
                          onClick={() => handleIngredientClick(pairing)}
                          className="bg-gradient-to-r from-yellow-200 to-yellow-300 text-black text-xs px-3 py-2 rounded-lg hover:from-yellow-300 hover:to-yellow-400 border border-black/20 transition-all duration-200 flex items-center gap-2 cursor-pointer font-medium shadow-sm"
                          title={`Buy ${pairing} at No Frills`}
                        >
                          <span>{pairing}</span>
                          <svg
                            className="w-3 h-3"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                          >
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth={2}
                              d="M3 3h2l.4 2M7 13h10l4-8H5.4m0 0L7 13m0 0l-2.5 5M7 13l2.5 5m6-5v6a2 2 0 01-2 2H9a2 2 0 01-2-2v-6m6 0V9a2 2 0 00-2-2H9a2 2 0 00-2 2v4.01"
                            />
                          </svg>
                        </button>
                      )
                    )}
                  </div>
                  <div className="mb-3">
                    <button
                      onClick={() => {
                        if (image.analysis?.food_pairings) {
                          const allPairings =
                            image.analysis.food_pairings.join(" ");
                          const encodedSearch = encodeURIComponent(allPairings);
                          const url = `https://www.nofrills.ca/search?search-bar=${encodedSearch}`;
                          window.open(url, "_blank");
                        }
                      }}
                      className="bg-gradient-to-r from-black to-gray-800 text-yellow-400 text-sm px-4 py-2 rounded-lg flex items-center gap-2 transition-all duration-200 border-2 border-black hover:from-gray-800 hover:to-black shadow-lg hover:shadow-xl font-semibold"
                      title="Buy all food pairings at No Frills"
                    >
                      <svg
                        className="w-4 h-4"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M3 3h2l.4 2M7 13h10l4-8H5.4m0 0L7 13m0 0l-2.5 5M7 13l2.5 5m6-5v6a2 2 0 01-2 2H9a2 2 0 01-2-2v-6m6 0V9a2 2 0 00-2-2H9a2 2 0 00-2 2v4.01"
                        />
                      </svg>
                      Buy All Pairings
                    </button>
                  </div>
                  <p className="text-xs text-black/60">
                    Click pairings to buy at No Frills
                  </p>
                </div>
              )}

            {/* Recipe */}
            {image.analysis.recipe && (
              <div className="mt-6">
                <span className="text-black font-semibold text-sm mb-3 block">
                  Recipe:
                </span>
                <div className="bg-white/70 rounded-lg p-4 border border-black/10">
                  <p className="text-black/80 leading-relaxed text-sm">
                    {image.analysis.recipe}
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
