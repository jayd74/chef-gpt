// ML Backend Configuration
const ML_BACKEND_URL =
  process.env.NEXT_PUBLIC_ML_BACKEND_URL || "http://localhost:8000";

export interface RecipeAnalysis {
  tags: string[];
  pairings: string[];
  nutrition?: NutritionInfo;
  difficulty?: "Easy" | "Medium" | "Hard";
  cuisine?: string;
  processing_time?: number;
}

export interface NutritionInfo {
  calories: number;
  protein: number;
  carbs: number;
  fat: number;
  fiber: number;
  sugar: number;
  sodium: number;
  per_serving: boolean;
}

export interface IngredientRecognition {
  ingredients: Array<{
    name: string;
    confidence: number;
    quantity?: string;
    unit?: string;
    bounding_box?: number[];
  }>;
  suggestions: string[];
  processing_time: number;
}

export interface MealPlanItem {
  title: string;
  description?: string;
  ingredients: string[];
  instructions: string[];
  tags: string[];
  cuisine?: string;
  difficulty?: string;
  prep_time?: number;
  cook_time?: number;
  servings?: number;
  calories?: number;
  confidence_score: number;
}

export interface DailyMealPlan {
  date: string;
  breakfast?: MealPlanItem;
  lunch?: MealPlanItem;
  dinner?: MealPlanItem;
  snacks?: MealPlanItem[];
  total_calories?: number;
}

export async function analyzeRecipeImage(
  imageFile: File
): Promise<IngredientRecognition> {
  try {
    const formData = new FormData();
    formData.append("file", imageFile);

    const response = await fetch(`${ML_BACKEND_URL}/analyze-food-image`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`ML Backend error: ${response.statusText}`);
    }

    const result = await response.json();
    return result as IngredientRecognition;
  } catch (error) {
    console.error("Error analyzing recipe image:", error);
    throw new Error("Failed to analyze recipe image");
  }
}

export async function generateRecipeTags(
  ingredients: Array<{ name: string; amount?: number; unit?: string }>,
  instructions: string[],
  cuisine?: string,
  category?: string
): Promise<string[]> {
  try {
    const response = await fetch(`${ML_BACKEND_URL}/generate-recipe-tags`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        ingredients,
        instructions,
        cuisine,
        category,
      }),
    });

    if (!response.ok) {
      throw new Error(`ML Backend error: ${response.statusText}`);
    }

    const tags = await response.json();
    return tags as string[];
  } catch (error) {
    console.error("Error generating recipe tags:", error);
    return [];
  }
}

export async function generatePairingSuggestions(
  ingredients: Array<{ name: string; amount?: number; unit?: string }>,
  cuisine?: string,
  category?: string
): Promise<string[]> {
  try {
    const response = await fetch(`${ML_BACKEND_URL}/generate-pairings`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        ingredients,
        cuisine,
        category,
      }),
    });

    if (!response.ok) {
      throw new Error(`ML Backend error: ${response.statusText}`);
    }

    const pairings = await response.json();
    return pairings as string[];
  } catch (error) {
    console.error("Error generating pairing suggestions:", error);
    return [];
  }
}

export async function calculateNutrition(
  ingredients: Array<{ name: string; amount?: number; unit?: string }>,
  servings: number = 1
): Promise<NutritionInfo> {
  try {
    const response = await fetch(`${ML_BACKEND_URL}/analyze-nutrition`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        ingredients,
        servings,
      }),
    });

    if (!response.ok) {
      throw new Error(`ML Backend error: ${response.statusText}`);
    }

    const result = await response.json();
    return result.nutrition as NutritionInfo;
  } catch (error) {
    console.error("Error calculating nutrition:", error);
    // Return default values if AI fails
    return {
      calories: 0,
      protein: 0,
      carbs: 0,
      fat: 0,
      fiber: 0,
      sugar: 0,
      sodium: 0,
      per_serving: true,
    };
  }
}

export async function findRecipesByCriteria(
  query: string,
  dietaryRestrictions?: string[],
  maxResults: number = 10
): Promise<
  Array<{
    title: string;
    description?: string;
    ingredients: string[];
    instructions: string[];
    tags: string[];
    cuisine?: string;
    difficulty?: string;
    prep_time?: number;
    cook_time?: number;
    servings?: number;
    confidence_score: number;
  }>
> {
  try {
    const response = await fetch(`${ML_BACKEND_URL}/recommend-recipes`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        query,
        dietary_restrictions: dietaryRestrictions || [],
        max_results: maxResults,
      }),
    });

    if (!response.ok) {
      throw new Error(`ML Backend error: ${response.statusText}`);
    }

    const result = await response.json();
    return result.recommendations;
  } catch (error) {
    console.error("Error finding recipes by criteria:", error);
    return [];
  }
}

export async function generateMealPlan(preferences: {
  dietaryRestrictions?: string[];
  cuisinePreferences?: string[];
  cookingTime?: number;
  servings?: number;
  days: number;
}): Promise<DailyMealPlan[]> {
  try {
    const response = await fetch(`${ML_BACKEND_URL}/generate-meal-plan`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        days: preferences.days,
        dietary_restrictions: preferences.dietaryRestrictions || [],
        cuisine_preferences: preferences.cuisinePreferences || [],
        cooking_time_limit: preferences.cookingTime,
        servings: preferences.servings || 1,
      }),
    });

    if (!response.ok) {
      throw new Error(`ML Backend error: ${response.statusText}`);
    }

    const result = await response.json();
    return result.meal_plan as DailyMealPlan[];
  } catch (error) {
    console.error("Error generating meal plan:", error);
    return [];
  }
}
