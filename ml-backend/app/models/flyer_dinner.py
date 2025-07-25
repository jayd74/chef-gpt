import os
from typing import List
from fastapi import FastAPI, HTTPException
from openai import OpenAI
from pydantic import BaseModel
import base64
import requests
import bs4
import pandas as pd
import secrets
from datetime import datetime

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])


BRANDS = {
    "t_t": "tt-supermarket-canada",
    "no_frills": "no-frills-canada", 
    "loblaws": "loblaws-canada"
}

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36"
]

async def get_html(url):
    """Simple HTML fetcher"""
    headers = {"User-Agent": secrets.choice(USER_AGENTS)}
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    return response.text

async def get_store_name(flyer_name):
    """Extract store name from flyer name"""
    if "T&T" in flyer_name:
        return "t_t"
    elif "No Frills" in flyer_name:
        return "no_frills"
    elif "Loblaws" in flyer_name:
        return "loblaws"
    return flyer_name.lower().replace(" ", "_")

async def is_ontario_flyer(flyer_name, store_name, flyer_url):
    """Check if flyer is from Ontario"""
    if store_name == "t_t":
        return True
    ontario_indicators = ["ontario", "on", "toronto", "gta"]
    text_to_check = (flyer_name + " " + flyer_url).lower()
    return any(indicator in text_to_check for indicator in ontario_indicators)

async def get_flyer_images(flyer_url):
    """Get flyer image URLs"""
    if not flyer_url:
        return []
    try:
        html = await get_html(f"{flyer_url}/all")
        soup = bs4.BeautifulSoup(html, "html.parser")
        container = soup.find("div", class_="bg-flyer-container")
        if not container:
            return []
        return [img.get("src") for img in container.find_all("img") if img.get("src")]
    except:
        return []

async def process_store(store_url):
    """Process one store - get first 3 flyers"""
    try:
        # Get store page
        html = await get_html(f"{store_url}/page/0")
        soup = bs4.BeautifulSoup(html, "html.parser")
        
        flyers = []
        count = 0
        
        for flyer_card in soup.select(".flyer-card")[:3]:  # Only first 3
            try:
                # Extract basic info
                flyer_name = flyer_card.find("h3").get_text(strip=True) if flyer_card.find("h3") else ""
                store_name = await get_store_name(flyer_name)
                flyer_url = flyer_card.find("a")["href"] if flyer_card.find("a") else ""
                
                # Check Ontario filter
                if not await is_ontario_flyer(flyer_name, store_name, flyer_url):
                    continue
                
                # Get images
                image_urls = await get_flyer_images(flyer_url)
                
                # Add to results
                for img_url in image_urls:
                    if img_url.lower().endswith(('.jpg', '.jpeg', '.png')):
                        flyers.append({
                            "flyer_image_url": img_url,
                            "store_name": store_name
                        })
                
                count += 1
                if count >= 3:
                    break
                    
            except Exception as e:
                continue
                
        print(f"Found {len(flyers)} flyers for {store_name}")
        return flyers
        
    except Exception as e:
        print(f"Error processing {store_url}: {e}")
        return []

async def scrape_flyers():
    """Main scraper function"""
    print("Starting flyer scraping...")
    
    all_flyers = []
    base_url = "https://flyers.smartcanucks.ca"
    
    for brand, path in BRANDS.items():
        store_url = f"{base_url}/{path}"
        print(f"Processing {brand}...")
        store_flyers = await process_store(store_url)
        all_flyers.extend(store_flyers)
    
    if all_flyers:
        # Save to CSV
        df = pd.DataFrame(all_flyers)
        filename = f"flyer_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df.to_csv(filename, index=False)
        print(f"Saved {len(all_flyers)} flyers to {filename}")
        return df
    else:
        print("No flyers found")
        return None

async def get_flyer_urls():
    try:
        df_flyer_urls = await scrape_flyers()
        banner_flyer_dict = {}
        for store, group_df in df_flyer_urls.groupby('store_name'):
            banner_flyer_dict[store] = group_df['flyer_image_url'].head(3).tolist()
        return banner_flyer_dict
    except Exception as e:
        print(f"Error getting flyer urls: {e}")
        banner_flyer_dict_fallback = {"no_frills":
                            ["https://flyers.smartcanucks.ca/uploads/pages/272912/no-frills-on-flyer-july-24-to-301-1.jpg",
                            "https://flyers.smartcanucks.ca/uploads/pages/272912/no-frills-on-flyer-july-24-to-301-2.jpg",
                            "https://flyers.smartcanucks.ca/uploads/pages/272912/no-frills-on-flyer-july-24-to-301-3.jpg"],
        "loblaws": ["https://flyers.smartcanucks.ca/uploads/pages/272915/loblaws-on-flyer-july-24-to-301-1.jpg",
        "https://flyers.smartcanucks.ca/uploads/pages/272915/loblaws-on-flyer-july-24-to-301-2.jpg",
        "https://flyers.smartcanucks.ca/uploads/pages/272915/loblaws-on-flyer-july-24-to-301-3.jpg"],
                    "t_t": ["https://flyers.smartcanucks.ca/uploads/pages/272705/tt-supermarket-gta-flyer-july-18-to-24-1.jpg",
                            "https://flyers.smartcanucks.ca/uploads/pages/272705/tt-supermarket-gta-flyer-july-18-to-24-2.jpg",
                            "https://flyers.smartcanucks.ca/uploads/pages/272705/tt-supermarket-gta-flyer-july-18-to-24-3.jpg"]}
        return banner_flyer_dict_fallback


async def generate_flyer_dinner(banner):
    banner_flyer_dict = await get_flyer_urls()
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