from openai import OpenAI
from dotenv import load_dotenv
import os
import time
import requests

load_dotenv()

gemini_api_key = os.getenv("GEMINI_API_KEY")

client = OpenAI(
    api_key=gemini_api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

def get_weather(city:str):
    url = f"https://wttr.in/{city.lower()}?format=%C+%t"
    try:
        responsee = requests.get(url)
        if responsee.status_code == 200:
            return f"Current Weather in {city}: {responsee.text}"
        
    except Exception as e:
        return e

def main():
    user_input = input("> :")
    for i in range(3):  
        try:
            response = client.chat.completions.create(
                model="gemini-2.0-flash",
                messages=[{"role": "user", "content": user_input}]
            )
            print(response.choices[0].message.content)
            break
        except Exception as e:
            print(f"Attempt {i+1} failed: {e}")
            time.sleep(2)

# main()

print(get_weather("New York"))
