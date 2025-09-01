from openai import OpenAI
from .bio import GEETANSH_BIO
from .config import API_KEY


def generate_response(question_name, options=None):
    client = OpenAI(
        api_key=API_KEY
    )
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": f"You are a job seeker assistant helping fill job applications based on this resume: {GEETANSH_BIO}",
            },
            {
                "role": "user",
                "content": f"Choose the most appropriate option for this question if provided. If not, answer concisely: '{question_name}'\nOptions: {options if options else 'None'}",
            },
        ],
        temperature=0.7,
        max_tokens=150,
    )
    return response.choices[0].message.content.strip()
