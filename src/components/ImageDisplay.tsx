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
    <div className="bg-white rounded-3xl shadow-lg hover:shadow-xl transition-all duration-300 overflow-hidden group">
      {/* Image */}
      <div className="relative">
        <img
          src={image.data}
          alt="Uploaded food"
          className="w-full h-64 object-cover group-hover:scale-105 transition-transform duration-300"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
        <div className="absolute top-4 right-4">
          <button
            onClick={() => onAnalyze()}
            disabled={isAnalyzing}
            className="bg-white/90 backdrop-blur-sm text-black hover:bg-white disabled:bg-gray-400 disabled:text-gray-600 px-4 py-2 rounded-full shadow-lg hover:shadow-xl transition-all duration-200 font-semibold text-sm flex items-center space-x-2"
          >
            {isAnalyzing ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-black" />
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

      {/* Content */}
      <div className="p-6">
        {/* Analysis Results */}
        {image.analysis ? (
          <div className="space-y-4">
            <div className="flex items-center space-x-2 mb-4">
              <div className="p-1.5 bg-yellow-100 rounded-full">
                <ChefHat className="h-4 w-4 text-black" />
              </div>
              <span className="text-sm font-semibold text-black">
                Recipe Analysis
              </span>
            </div>

            {/* Dish Name and Description */}
            <div className="mb-4">
              <h4 className="font-bold text-black text-lg mb-2">
                {image.analysis.dish_name || "Unknown Dish"}
              </h4>
              {image.analysis.description && (
                <p className="text-black/70 text-sm leading-relaxed">
                  {image.analysis.description}
                </p>
              )}
            </div>

            {/* Tags */}
            {image.analysis.tags && image.analysis.tags.length > 0 && (
              <div className="mb-4">
                <div className="flex flex-wrap gap-1.5">
                  {image.analysis.tags.map((tag: string, index: number) => (
                    <span
                      key={index}
                      className="bg-yellow-100 text-black text-xs px-2 py-1 rounded-full font-medium"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Quick Nutrition */}
            {image.analysis.nutrition_facts && (
              <div className="mb-4 p-3 bg-yellow-50 rounded-2xl">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-black/60">Calories</span>
                  <span className="font-bold text-black">
                    {image.analysis.nutrition_facts.calories} kcal
                  </span>
                </div>
                <div className="flex items-center justify-between text-sm mt-1">
                  <span className="text-black/60">Protein</span>
                  <span className="font-bold text-black">
                    {image.analysis.nutrition_facts.protein}g
                  </span>
                </div>
              </div>
            )}

            {/* Ingredients Preview */}
            {image.analysis.ingredients &&
              image.analysis.ingredients.length > 0 && (
                <div className="mb-4">
                  <h5 className="font-semibold text-black text-sm mb-2">
                    Ingredients
                  </h5>
                  <div className="flex flex-wrap gap-1.5">
                    {image.analysis.ingredients
                      .slice(0, 3)
                      .map((ingredient: string, index: number) => (
                        <button
                          key={index}
                          onClick={() => handleIngredientClick(ingredient)}
                          className="bg-white text-black text-xs px-2 py-1 rounded-full hover:bg-yellow-100 border border-black/10 transition-colors cursor-pointer"
                          title={`Buy ${ingredient} at No Frills`}
                        >
                          {ingredient}
                        </button>
                      ))}
                    {image.analysis.ingredients.length > 3 && (
                      <span className="text-xs text-black/60 px-2 py-1">
                        +{image.analysis.ingredients.length - 3} more
                      </span>
                    )}
                  </div>
                  <button
                    onClick={handleBuyAllIngredients}
                    className="mt-2 w-full bg-black text-yellow-400 text-xs px-3 py-2 rounded-full hover:bg-gray-800 transition-colors font-semibold"
                    title="Buy all ingredients at No Frills"
                  >
                    Buy All Ingredients
                  </button>
                </div>
              )}

            {/* Food Pairings Preview */}
            {image.analysis.food_pairings &&
              image.analysis.food_pairings.length > 0 && (
                <div className="mb-4">
                  <h5 className="font-semibold text-black text-sm mb-2">
                    Goes well with
                  </h5>
                  <div className="flex flex-wrap gap-1.5">
                    {image.analysis.food_pairings
                      .slice(0, 3)
                      .map((pairing: string, index: number) => (
                        <button
                          key={index}
                          onClick={() => handleIngredientClick(pairing)}
                          className="bg-yellow-100 text-black text-xs px-2 py-1 rounded-full hover:bg-yellow-200 transition-colors cursor-pointer"
                          title={`Buy ${pairing} at No Frills`}
                        >
                          {pairing}
                        </button>
                      ))}
                    {image.analysis.food_pairings.length > 3 && (
                      <span className="text-xs text-black/60 px-2 py-1">
                        +{image.analysis.food_pairings.length - 3} more
                      </span>
                    )}
                  </div>
                </div>
              )}

            {/* Recipe Preview */}
            {image.analysis.recipe && (
              <div>
                <h5 className="font-semibold text-black text-sm mb-2">
                  Recipe
                </h5>
                <p className="text-black/70 text-sm leading-relaxed line-clamp-3">
                  {image.analysis.recipe}
                </p>
              </div>
            )}
          </div>
        ) : (
          <div className="text-center py-8">
            <div className="p-3 bg-yellow-100 rounded-full w-12 h-12 mx-auto mb-3 flex items-center justify-center">
              <ChefHat className="h-6 w-6 text-black" />
            </div>
            <p className="text-black/60 text-sm">Ready for analysis</p>
          </div>
        )}
      </div>
    </div>
  );
}
