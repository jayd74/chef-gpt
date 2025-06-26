"use client";

import { useState } from "react";
import { ChefHat, X } from "lucide-react";
import ReactMarkdown from "react-markdown";

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
  const [showModal, setShowModal] = useState(false);

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

  const handleViewFullAnalysis = () => {
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
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
                <div className="text-black/70 leading-relaxed">
                  <ReactMarkdown>{image.analysis.description}</ReactMarkdown>
                </div>
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
              <div className="mb-4">
                <h5 className="font-semibold text-black text-sm mb-2">
                  Recipe
                </h5>
                <p className="text-black/70 text-sm leading-relaxed line-clamp-3">
                  {image.analysis.recipe}
                </p>
              </div>
            )}

            {/* View More CTA */}
            <div className="pt-2 border-t border-black/10">
              <button
                onClick={handleViewFullAnalysis}
                className="w-full bg-yellow-100 text-black hover:bg-yellow-200 text-sm px-4 py-2 rounded-full transition-colors font-semibold flex items-center justify-center space-x-2"
              >
                <span>View Full Analysis</span>
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
                    d="M9 5l7 7-7 7"
                  />
                </svg>
              </button>
            </div>
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

      {/* Full Analysis Modal */}
      {showModal && image.analysis && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-3xl max-w-2xl w-full max-h-[90vh] overflow-y-auto shadow-2xl">
            {/* Modal Header */}
            <div className="sticky top-0 bg-white border-b border-black/10 p-6 rounded-t-3xl">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div className="p-2 bg-yellow-100 rounded-full">
                    <ChefHat className="h-5 w-5 text-black" />
                  </div>
                  <div>
                    <h3 className="text-xl font-bold text-black">
                      Full Recipe Analysis
                    </h3>
                    <p className="text-sm text-black/60">
                      Complete AI-powered insights
                    </p>
                  </div>
                </div>
                <button
                  onClick={closeModal}
                  className="p-2 hover:bg-black/10 rounded-full transition-colors"
                >
                  <X className="h-5 w-5 text-black" />
                </button>
              </div>
            </div>

            {/* Modal Content */}
            <div className="p-6 space-y-6">
              {/* Dish Image */}
              <div className="relative">
                <img
                  src={image.data}
                  alt="Food dish"
                  className="w-full h-48 object-cover rounded-2xl shadow-lg"
                />
              </div>

              {/* Dish Name and Description */}
              <div>
                <h2 className="text-2xl font-bold text-black mb-3">
                  {image.analysis.dish_name || "Unknown Dish"}
                </h2>
                {image.analysis.description && (
                  <div className="text-black/70 leading-relaxed">
                    <ReactMarkdown>{image.analysis.description}</ReactMarkdown>
                  </div>
                )}
              </div>

              {/* Tags */}
              {image.analysis.tags && image.analysis.tags.length > 0 && (
                <div>
                  <h4 className="font-semibold text-black mb-3">Tags</h4>
                  <div className="flex flex-wrap gap-2">
                    {image.analysis.tags.map((tag: string, index: number) => (
                      <span
                        key={index}
                        className="bg-yellow-100 text-black px-3 py-1 rounded-full text-sm font-medium"
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Nutrition Facts */}
              {image.analysis.nutrition_facts && (
                <div>
                  <h4 className="font-semibold text-black mb-3">
                    Nutrition Facts
                  </h4>
                  <div className="bg-yellow-50 rounded-2xl p-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <span className="text-black/60 text-sm">
                          Serving Size
                        </span>
                        <p className="font-bold text-black">
                          {image.analysis.nutrition_facts.serving_size}
                        </p>
                      </div>
                      <div>
                        <span className="text-black/60 text-sm">Calories</span>
                        <p className="font-bold text-black">
                          {image.analysis.nutrition_facts.calories} kcal
                        </p>
                      </div>
                      <div>
                        <span className="text-black/60 text-sm">Protein</span>
                        <p className="font-bold text-black">
                          {image.analysis.nutrition_facts.protein}g
                        </p>
                      </div>
                      <div>
                        <span className="text-black/60 text-sm">
                          Carbohydrates
                        </span>
                        <p className="font-bold text-black">
                          {image.analysis.nutrition_facts.carbohydrates}g
                        </p>
                      </div>
                      <div>
                        <span className="text-black/60 text-sm">Fat</span>
                        <p className="font-bold text-black">
                          {image.analysis.nutrition_facts.fat}g
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Ingredients */}
              {image.analysis.ingredients &&
                image.analysis.ingredients.length > 0 && (
                  <div>
                    <h4 className="font-semibold text-black mb-3">
                      Ingredients
                    </h4>
                    <div className="flex flex-wrap gap-2 mb-4">
                      {image.analysis.ingredients.map(
                        (ingredient: string, index: number) => (
                          <button
                            key={index}
                            onClick={() => handleIngredientClick(ingredient)}
                            className="bg-white text-black px-3 py-2 rounded-full hover:bg-yellow-100 border border-black/10 transition-colors cursor-pointer font-medium"
                            title={`Buy ${ingredient} at No Frills`}
                          >
                            {ingredient}
                          </button>
                        )
                      )}
                    </div>
                    <button
                      onClick={handleBuyAllIngredients}
                      className="bg-black text-yellow-400 px-4 py-2 rounded-full hover:bg-gray-800 transition-colors font-semibold"
                      title="Buy all ingredients at No Frills"
                    >
                      Buy All Ingredients
                    </button>
                  </div>
                )}

              {/* Food Pairings */}
              {image.analysis.food_pairings &&
                image.analysis.food_pairings.length > 0 && (
                  <div>
                    <h4 className="font-semibold text-black mb-3">
                      Goes well with
                    </h4>
                    <div className="flex flex-wrap gap-2">
                      {image.analysis.food_pairings.map(
                        (pairing: string, index: number) => (
                          <button
                            key={index}
                            onClick={() => handleIngredientClick(pairing)}
                            className="bg-yellow-100 text-black px-3 py-2 rounded-full hover:bg-yellow-200 transition-colors cursor-pointer font-medium"
                            title={`Buy ${pairing} at No Frills`}
                          >
                            {pairing}
                          </button>
                        )
                      )}
                    </div>
                  </div>
                )}

              {/* Recipe */}
              {image.analysis.recipe && (
                <div>
                  <h4 className="font-semibold text-black mb-3">Recipe</h4>
                  <div className="bg-white/50 rounded-2xl p-4 border border-black/10">
                    <ReactMarkdown>{image.analysis.recipe}</ReactMarkdown>
                  </div>
                </div>
              )}
            </div>

            {/* Modal Footer */}
            <div className="sticky bottom-0 bg-white border-t border-black/10 p-6 rounded-b-3xl">
              <button
                onClick={closeModal}
                className="w-full bg-black text-yellow-400 hover:bg-gray-800 px-6 py-3 rounded-full font-semibold transition-colors"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
