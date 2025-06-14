import asyncio
from random import randint
import requests
import base64
from happy.env import Keys

API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
headers = {"Authorization": f"Bearer {Keys['HuggingFace']}"}
    
async def query(payload):
    response = await asyncio.to_thread(requests.post, API_URL, headers=headers, json=payload)
    return response.content

async def generate_images(prompt:str) -> list[str]:
    """
    returns a list of base64 encoded image URLs
    """
    tasks = []
    results = []
    for _ in range(1):
        payload = {
            "inputs": f"{prompt}, quality=4K, sharpness=maximum, details=Ultra High, resolution=high, seed = {randint(0, 10000)}",
        }
        task = asyncio.create_task(query(payload))
        tasks.append(task)

    image_bytes_list = await asyncio.gather(*tasks)

    for image_bytes in image_bytes_list:
        base64_image = base64.b64encode(image_bytes).decode('utf-8')
        results.append(base64_image)
    return results

def generateImages(prompt:str):
    r = asyncio.run(generate_images(prompt))
    return r





if __name__ == "__main__":
    print(generateImages("iron man"))
