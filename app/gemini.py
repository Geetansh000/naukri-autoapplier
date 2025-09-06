import os
import google.generativeai as genai
import re
from .bio import GEETANSH_BIO
from .config import GOOGLE_API_KEY

# Load resume
# with open("resume.json", "r") as f:
#     resume_json = json.load(f)
# resume_json_str = json.dumps(resume_json, indent=2)

genai.configure(api_key=GOOGLE_API_KEY)

generation_config = {
    "temperature": 0.3,  # Lower = more deterministic
    "top_p": 0.9,
    "top_k": 40,
    "max_output_tokens": 200,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
    system_instruction="""
You are Geetansh Sharma, a backend developer.
Answer strictly from the resume.
Rules:
- For multiple choice: return ONLY the correct option
- For yes/no: return 'Yes' or 'No'
- For years of experience: return only the number (e.g., 2)
- If multiple technologies are listed (e.g., 'Node.js / Python'), assume they are similar and return the common experience: 2
- For dates: YYYY-MM-DD
- Otherwise: 1–5 words, no explanations
- Never use punctuation, quotes, or extra text
"""
)

chat_session = model.start_chat(
    history=[
        {"role": "user", "parts": [GEETANSH_BIO]},
        {"role": "model", "parts": ["Resume loaded."]},

        {"role": "user", "parts": [
            "All skills have 2 years of experience unless stated."]},
        {"role": "model", "parts": ["Understood."]},

        {"role": "user", "parts": [
            "From now on, follow the output rules strictly."]},
        {"role": "model", "parts": ["Ready to answer."]}
    ]
)


def bard_flash_response(question) -> str:
    try:
        response = chat_session.send_message(question)
        raw_text = response.text.strip()
        print(f"🤖 AI Raw: '{raw_text}'")

        # If the question is about "experience" or "years", we want a single digit
        if any(word in question.lower() for word in ['experience', 'years', 'year', 'how long']):
            # Extract all numbers
            numbers = re.findall(r'\b\d+\b', raw_text)
            # Return the first number that makes sense (1-5 years)
            for num in numbers:
                n = int(num)
                if 1 <= n <= 5:
                    return num
            return "2"  # fallback: you have ~2 years

        # For multiple choice (has "1.", "2.", etc.)
        if re.search(r'\b\d+\.', question):
            numbers = re.findall(r'\b\d+\b', raw_text)
            return numbers[0] if numbers else "1"

        # Clean up text answers
        cleaned = re.sub(r'[^\w\s]', '', raw_text).strip()
        return cleaned or "Not available"

    except Exception as e:
        print(f"❌ AI Error: {e}")
        return "2"  # safest fallback for experience
