import os
from typing import List
from fastapi import FastAPI, HTTPException
from openai import OpenAI
from pydantic import BaseModel
import base64
import requests

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])


async def generate_flyer_dinner(flyer_url):
    if not flyer_url:
        flyer_url = "https://flyers.smartcanucks.ca/uploads/pages/270945/no-frills-west-flyer-june-26-to-july-23-1.jpg"
    # image_base64 = image_url_to_base64()
    response = client.responses.create(
        model="gpt-4.1-mini",
        input=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": "Extract the products on this flyer. Generate one dinner plan for 2 that utilizes these products as much as possible. The ingredients in the recipe need to match the flyer's product name if the ingredient comes from the flyer product. Estimate the cost of the dinner.",
                    },
                    {
                        "type": "input_image",
                        # "image_url": f"{image_url}",
                        "image_url": flyer_url
                    },
                ],
            }
        ],
        text={
            "format": {
                "type": "json_schema",
                "name": "flyer_dinner",
                "schema": {
                    "type": "object",
                    "properties": {
                        "dish_name": {"type": "string"},
                        "description": {"type": "string"},
                        "tags": {"type": "array", "items": {"type": "string"}},
                        "recipe": {"type": "string"},
                        "ingredients": {"type": "array", "items": {"type": "string"}},
                        "cost": {"type": "integer"},
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
                    },
                    "required": [
                        "dish_name",
                        "description",
                        "tags",
                        "recipe",
                        "ingredients",
                        "nutrition_facts",
                        "cost",
                    ],  # Added to required
                    "additionalProperties": False,
                },
                "strict": True,
            }
        },
    )
    return response.output_text

