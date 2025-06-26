import os
from typing import List
from fastapi import FastAPI, HTTPException
from openai import OpenAI
from pydantic import BaseModel
import base64
import requests

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
banner_flyer_dict = {"no_frills":
                     ["https://flyers.smartcanucks.ca/uploads/pages/270945/no-frills-west-flyer-june-26-to-july-23-2.jpg",
"https://flyers.smartcanucks.ca/uploads/pages/270945/no-frills-west-flyer-june-26-to-july-23-1.jpg",
"https://flyers.smartcanucks.ca/uploads/pages/270945/no-frills-west-flyer-june-26-to-july-23-3.jpg"],
"loblaws": ["https://flyers.smartcanucks.ca/uploads/pages/270962/loblaws-on-flyer-june-26-to-july-21-1.jpg",
            "https://flyers.smartcanucks.ca/uploads/pages/270962/loblaws-on-flyer-june-26-to-july-21-2.jpg",
            "https://flyers.smartcanucks.ca/uploads/pages/270962/loblaws-on-flyer-june-26-to-july-21-3.jpg"],
            "t_t": ["https://flyers.smartcanucks.ca/uploads/pages/270683/tt-supermarket-gta-flyer-june-20-to-261-1.jpg",
                    "https://flyers.smartcanucks.ca/uploads/pages/270683/tt-supermarket-gta-flyer-june-20-to-261-2.jpg",
                    "https://flyers.smartcanucks.ca/uploads/pages/270683/tt-supermarket-gta-flyer-june-20-to-261-3.jpg"]}

async def generate_flyer_dinner(banner):
    urls = banner_flyer_dict[banner]
    response = client.responses.create(
        model="gpt-4.1-mini",
        input=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": "Extract all products listed in these flyers. Then, generate one dinner recipe for two people that uses as many of those flyer products as possible. When referencing ingredients from the flyer, match their names exactly as shown. Finally, estimate the total cost of the dinner based on the flyer prices.",
                    },
                    {
                        "type": "input_image",
                        "image_url": urls[0]
                    },
                    {
                        "type": "input_image",
                        "image_url": urls[1]
                    },
                    {
                        "type": "input_image",
                        "image_url": urls[2]
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
    return {"llm_response": response.output_text,
            "urls":
            {"url1": urls[0],
            "url2": urls[1],
            "url3": urls[2]}}