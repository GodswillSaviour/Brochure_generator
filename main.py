import os
from openai import OpenAI
from scraper import fetch_website_contents
from dotenv import load_dotenv

load_dotenv(override=True)
api_key = os.getenv('OPENAI_API_KEY')

if not api_key:
    print("api key not found")
elif not api_key.startswith("sk-proj"):
    print("api key doesnt start with sk-proj")
elif api_key.strip() != api_key:
    print("invalid api key")
else:
    print("Api key found")

openai = OpenAI()
system_prompt ="""you are an AI assistant that helps summarize the contents of a website in a user friendly explanation"""
user_prompt = """help me summarize the contents of the website"""


def message_for(website):
    return [{"role":"system", "content":system_prompt}, 
            {"role":"user","content":user_prompt + website }]


def summarize(url):
    website = fetch_website_contents(url)
    response = openai.chat.completions.create(model="gpt-4.1-nano", messages=message_for(website))
    return response.choices[0].message.content



print(summarize("https://edwarddonner.com"))
