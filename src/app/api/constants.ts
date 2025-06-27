// ML Backend Configuration
export const ML_BACKEND_URL = "https://chef-gpt-c4sc.onrender.com";

// API Endpoints
export const API_ENDPOINTS = {
  FLYER_DINNER: `${ML_BACKEND_URL}/flyer_dinner`,
  RECIPE_ANALYSIS: `${ML_BACKEND_URL}/recipe_analysis`,
  CHAT: `${ML_BACKEND_URL}/chat`,
  CHAT_SIMPLE: `${ML_BACKEND_URL}/chat/simple`,
  HEALTH: `${ML_BACKEND_URL}/health`,
} as const;

// App Configuration
export const APP_CONFIG = {
  NAME: "ChefGPT",
  DESCRIPTION: "AI-powered cooking assistant",
  VERSION: "1.0.0",
} as const;
