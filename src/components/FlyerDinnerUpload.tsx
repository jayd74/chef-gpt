"use client";

import { useState } from "react";
import { Loader2, Link, X, Maximize2 } from "lucide-react";
import ReactMarkdown from "react-markdown";
import Image from "next/image";

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

interface FlyerResponse {
  llm_response: string;
  urls: {
    url1?: string;
    url2?: string;
    url3?: string;
    [key: string]: string | undefined;
  };
}

interface FlyerDinnerUploadProps {
  onAnalysisComplete?: (analysis: FlyerAnalysis) => void;
}

export default function FlyerDinnerUpload({
  onAnalysisComplete,
}: FlyerDinnerUploadProps) {
  const [flyerUrl, _setFlyerUrl] = useState<string>("");
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysis, setAnalysis] = useState<FlyerAnalysis | null>(null);
  const [flyerUrls, setFlyerUrls] = useState<string[]>([]);
  const [_error, setError] = useState<string | null>(null);
  const [showModal, setShowModal] = useState(false);
  const [selectedImage, setSelectedImage] = useState<string>("");
  const [selectedBanner, setSelectedBanner] = useState<string>("");

  const analyzeFlyer = async (banner?: string) => {
    if (!flyerUrl.trim() && !banner) {
      setError("Please enter a flyer URL or select a banner");
      return;
    }

    setIsAnalyzing(true);
    setError(null);

    try {
      const payload = banner ? { banner } : { flyer_url: flyerUrl.trim() };

      const response = await fetch("/api/flyer-dinner", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error("Failed to analyze flyer");
      }

      const data: FlyerResponse = await response.json();

      // Parse the llm_response JSON string
      const parsedAnalysis: FlyerAnalysis = JSON.parse(data.llm_response);

      // Extract flyer URLs
      const urls = Object.values(data.urls).filter((url) => url) as string[];
      setFlyerUrls(urls);

      setAnalysis(parsedAnalysis);
      onAnalysisComplete?.(parsedAnalysis);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleBannerClick = (banner: string) => {
    setSelectedBanner(banner);
    analyzeFlyer(banner);
  };

  const handleIngredientClick = (ingredient: string) => {
    const encodedSearch = encodeURIComponent(ingredient);

    // Determine the store URL based on the selected banner
    let storeUrl: string;
    switch (selectedBanner) {
      case "no_frills":
        storeUrl = `https://www.nofrills.ca/search?search-bar=${encodedSearch}`;
        break;
      case "loblaws":
        storeUrl = `https://www.loblaws.ca/search?search-bar=${encodedSearch}`;
        break;
      case "t_t":
        storeUrl = `https://www.tntsupermarket.com/eng/search.html?query=${encodedSearch}`;
        break;
      default:
        // Default to No Frills if no banner is selected
        storeUrl = `https://www.nofrills.ca/search?search-bar=${encodedSearch}`;
    }

    window.open(storeUrl, "_blank");
  };

  const openModal = (imageUrl?: string) => {
    if (imageUrl) {
      setSelectedImage(imageUrl);
    }
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
    setSelectedImage("");
  };

  return (
    <div className="w-full max-w-4xl mx-auto">
      {/* Banner Buttons Section */}
      <div className="bg-white rounded-3xl shadow-lg p-6 mb-6 border border-black/10">
        <h3 className="text-xl font-bold text-black mb-4">
          Quick Flyer Analysis
        </h3>
        <p className="text-black/70 mb-6">
          Select a grocery store banner to get recipe suggestions based on their
          current flyer
        </p>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* No Frills */}
          <button
            onClick={() => handleBannerClick("no_frills")}
            disabled={isAnalyzing}
            className="group relative border-2 border-[#FEE600] rounded-2xl p-6 hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
            style={{ backgroundColor: "#FEE600" }}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = "#e6cf00";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = "#FEE600";
            }}
          >
            <div className="flex flex-col items-center space-y-3">
              <div className="w-16 h-16 bg-white rounded-full flex items-center justify-center group-hover:scale-110 transition-transform overflow-hidden">
                <Image
                  src="/nofrills-logo.jpg"
                  alt="No Frills Logo"
                  width={64}
                  height={64}
                  className="w-full h-full object-contain"
                />
              </div>
              <div className="text-center">
                <h4 className="font-bold text-black text-lg">No Frills</h4>
              </div>
            </div>
          </button>

          {/* Loblaws */}
          <button
            onClick={() => handleBannerClick("loblaws")}
            disabled={isAnalyzing}
            className="group relative border-2 border-[#ed1b23] rounded-2xl p-6 hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
            style={{ backgroundColor: "#ed1b23" }}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = "#b3141a";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = "#ed1b23";
            }}
          >
            <div className="flex flex-col items-center space-y-3">
              <div className="w-16 h-16 bg-white rounded-full flex items-center justify-center group-hover:scale-110 transition-transform overflow-hidden">
                <Image
                  src="/Loblaws-scaled.webp"
                  alt="Loblaws Logo"
                  width={64}
                  height={64}
                  className="w-full h-full object-contain"
                />
              </div>
              <div className="text-center">
                <h4 className="font-bold text-white text-lg">Loblaws</h4>
              </div>
            </div>
          </button>

          {/* T&T */}
          <button
            onClick={() => handleBannerClick("t_t")}
            disabled={isAnalyzing}
            className="group relative border-2 border-[#007852] rounded-2xl p-6 hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
            style={{ backgroundColor: "#007852" }}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = "#005a3a";
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = "#007852";
            }}
          >
            <div className="flex flex-col items-center space-y-3">
              <div className="w-16 h-16 bg-white rounded-full flex items-center justify-center group-hover:scale-110 transition-transform overflow-hidden">
                <Image
                  src="/tnt-logo.png"
                  alt="tnt Logo"
                  width={64}
                  height={64}
                  className="w-full h-full object-contain"
                />
              </div>
              <div className="text-center">
                <h4 className="font-bold text-white text-lg">
                  T&T Supermarket
                </h4>
              </div>
            </div>
          </button>
        </div>

        {isAnalyzing && (
          <div className="mt-6 text-center">
            <div className="inline-flex items-center gap-2 bg-yellow-100 px-4 py-2 rounded-full">
              <Loader2 className="w-4 h-4 animate-spin text-black" />
              <span className="text-black font-medium">Analyzing flyer...</span>
            </div>
          </div>
        )}
      </div>

      {/* Thumbnail Preview Section */}
      {flyerUrls.length > 0 && !isAnalyzing && (
        <div className="bg-white rounded-3xl shadow-lg p-6 mb-6 border border-black/10">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-xl font-bold text-black">Flyer Gallery</h3>
            <span className="text-sm text-black/60">
              {flyerUrls.length} pages
            </span>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {flyerUrls.map((url, index) => (
              <div key={index} className="relative">
                <div
                  className="w-full h-32 rounded-2xl overflow-hidden shadow-md cursor-pointer hover:shadow-lg transition-shadow"
                  onClick={() => openModal(url)}
                >
                  <Image
                    src={url}
                    alt={`Flyer page ${index + 1}`}
                    width={400}
                    height={128}
                    className="w-full h-full object-cover"
                    unoptimized
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
                <div className="absolute top-2 right-2 bg-black/70 text-white text-xs px-2 py-1 rounded-full">
                  Page {index + 1}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Legacy URL Preview Section */}
      {flyerUrl && !isAnalyzing && flyerUrls.length === 0 && (
        <div className="bg-white rounded-3xl shadow-lg p-6 mb-6 border border-black/10">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-xl font-bold text-black">Flyer Preview</h3>
            <button
              onClick={() => openModal(flyerUrl)}
              className="p-2 bg-yellow-100 rounded-full hover:bg-yellow-200 transition-colors"
              title="View larger image"
            >
              <Maximize2 className="w-4 h-4 text-black" />
            </button>
          </div>
          <div className="relative">
            <div
              className="w-48 h-32 rounded-2xl overflow-hidden shadow-md cursor-pointer hover:shadow-lg transition-shadow"
              onClick={() => openModal(flyerUrl)}
            >
              <Image
                src={flyerUrl}
                alt="Flyer preview"
                width={192}
                height={128}
                className="w-full h-full object-cover"
                unoptimized
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
              <Image
                src={selectedImage}
                alt="Flyer full view"
                width={800}
                height={600}
                className="w-full h-auto rounded-2xl shadow-lg"
                unoptimized
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
