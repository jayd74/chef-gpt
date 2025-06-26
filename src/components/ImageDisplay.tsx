"use client";

import { useState } from "react";
import { Sparkles, Clock, ChefHat, Trash2 } from "lucide-react";
import { Button } from "@/components/ui/button";

interface FoodImage {
  id: string;
  base64: string;
  filename: string;
  uploadedAt: Date;
  analysis?: any;
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
  const [isExpanded, setIsExpanded] = useState(false);

  const formatDate = (date: Date) => {
    return new Intl.DateTimeFormat("en-US", {
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    }).format(date);
  };

  return (
    <div className="bg-gray-50 rounded-lg p-4 border">
      <div className="flex items-start space-x-4">
        {/* Image */}
        <div className="flex-shrink-0">
          <img
            src={image.base64}
            alt={image.filename}
            className="w-20 h-20 object-cover rounded-lg border"
            onClick={() => setIsExpanded(!isExpanded)}
            style={{ cursor: "pointer" }}
          />
        </div>

        {/* Content */}
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <h3 className="text-sm font-medium text-gray-900 truncate">
                {image.filename}
              </h3>
              <p className="text-xs text-gray-500 mt-1">
                Uploaded {formatDate(image.uploadedAt)}
              </p>
            </div>

            <div className="flex items-center space-x-2">
              {!image.analysis && (
                <Button
                  size="sm"
                  onClick={onAnalyze}
                  disabled={isAnalyzing}
                  className="bg-orange-600 hover:bg-orange-700"
                >
                  {isAnalyzing ? (
                    <>
                      <div className="animate-spin rounded-full h-3 w-3 border-b-2 border-white mr-1" />
                      Analyzing...
                    </>
                  ) : (
                    <>
                      <Sparkles className="h-3 w-3 mr-1" />
                      Analyze
                    </>
                  )}
                </Button>
              )}
            </div>
          </div>

          {/* Analysis Results */}
          {image.analysis && (
            <div className="mt-3 space-y-2">
              <div className="flex items-center space-x-2">
                <ChefHat className="h-4 w-4 text-orange-600" />
                <span className="text-sm font-medium text-gray-900">
                  Analysis Complete
                </span>
              </div>

              <div className="bg-white rounded p-3 border">
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span className="text-gray-500">Detected Food:</span>
                    <p className="font-medium text-gray-900">
                      {image.analysis.dish_name || "Unknown"}
                    </p>
                  </div>
                  {image.analysis.calories && (
                    <div>
                      <span className="text-gray-500">Calories:</span>
                      <p className="font-medium text-gray-900">
                        {image.analysis.calories} kcal
                      </p>
                    </div>
                  )}
                  {image.analysis.cooking_time && (
                    <div>
                      <span className="text-gray-500">Cooking Time:</span>
                      <p className="font-medium text-gray-900">
                        {image.analysis.cooking_time} min
                      </p>
                    </div>
                  )}
                </div>

                {image.analysis.ingredients && (
                  <div className="mt-3">
                    <span className="text-gray-500 text-sm">Ingredients:</span>
                    <p className="text-sm text-gray-900 mt-1">
                      {image.analysis.ingredients.join(", ")}
                    </p>
                  </div>
                )}

                {image.analysis.recipe && (
                  <div className="mt-3">
                    <span className="text-gray-500 text-sm">Recipe:</span>
                    <p className="text-sm text-gray-900 mt-1">
                      {image.analysis.recipe}
                    </p>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Expanded Image Modal */}
      {isExpanded && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
          onClick={() => setIsExpanded(false)}
        >
          <div className="max-w-4xl max-h-[90vh] p-4">
            <img
              src={image.base64}
              alt={image.filename}
              className="max-w-full max-h-full object-contain rounded-lg"
              onClick={(e) => e.stopPropagation()}
            />
          </div>
        </div>
      )}
    </div>
  );
}
