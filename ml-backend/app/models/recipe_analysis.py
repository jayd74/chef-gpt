import os
from fastapi import FastAPI, HTTPException
from openai import OpenAI
from pydantic import BaseModel


client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])


async def analyze_food_image(base64_image: str):
    response = client.responses.create(
        model="gpt-4.1-mini",
        input=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": "Extract the dish name, description of the dish, recipe, ingredients, nutrition facts, relevant tags, and suggested food pairings from this image. Keep the description short and sweet. Return the recipe in steps as html list format.",
                    },
                    {
                        "type": "input_image",
                        "image_url": f"{base64_image}",
                    },
                ],
            }
        ],
        text={
            "format": {
                "type": "json_schema",
                "name": "food_analysis",
                "schema": {
                    "type": "object",
                    "properties": {
                        "dish_name": {"type": "string"},
                        "description": {"type": "string"},
                        "tags": {"type": "array", "items": {"type": "string"}},
                        "recipe": {"type": "string"},
                        "ingredients": {"type": "array", "items": {"type": "string"}},
                        "nutrition_facts": {
                            "type": "object",
                            "properties": {
                                "serving_size": {"type": "string"},
                                "calories": {"type": "integer"},
                                "protein": {"type": "integer"},
                                "carbohydrates": {"type": "integer"},
                                "fat": {"type": "integer"},
                            },
                            "required": [
                                "serving_size",
                                "calories",
                                "protein",
                                "carbohydrates",
                                "fat",
                            ],
                            "additionalProperties": False,
                        },
                        "food_pairings": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                    },
                    "required": [
                        "dish_name",
                        "description",
                        "tags",
                        "recipe",
                        "ingredients",
                        "nutrition_facts",
                        "food_pairings",
                    ],  # Added to required
                    "additionalProperties": False,
                },
                "strict": True,
            }
        },
    )
    return response.output_text
