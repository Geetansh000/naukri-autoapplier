from openai import OpenAI
from .bio import BIO
from .config import API_KEY, AUTHOR_NAME
import re
import time


def generate_response(question_name, options=None) -> str:
    client = OpenAI(api_key=API_KEY)

    system_instruction = f"""
You are {AUTHOR_NAME}, a backend developer.
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

    user_prompt = f"Choose the most appropriate option for this question if provided. If not, answer concisely: '{question_name}'\nOptions: {options if options else 'None'}"

    max_retries = 3
    retry_delay = 2

    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {"role": "system", "content": system_instruction +
                        "\nResume:\n" + BIO},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.3,
                max_tokens=200,
            )

            raw = response.choices[0].message.content.strip()
            print(f"🤖 AI Raw: '{raw}'")

            qlower = question_name.lower()

            # If the question is about experience or years, return a single sensible number
            if any(w in qlower for w in ["experience", "years", "year", "how long"]):
                numbers = re.findall(r'\b\d+\b', raw)
                for num in numbers:
                    n = int(num)
                    if 1 <= n <= 20:
                        return str(n)
                return "2"

            # If question looks like multiple choice (has '1.' '2.' etc.), return the chosen option number
            if re.search(r'\b\d+\.', question_name):
                numbers = re.findall(r'\b\d+\b', raw)
                return numbers[0] if numbers else "1"

            # Yes/no explicit handling: prefer exact Yes/No
            if any(w in qlower for w in ["yes or no", "yes/no", "is the", "does the", "do you", "have you", "can you"]) or (qlower.strip().endswith("?") and len(raw.split()) == 1):
                low = raw.lower()
                if "yes" in low:
                    return "Yes"
                if "no" in low:
                    return "No"

            # Clean up: remove punctuation, keep words
            cleaned = re.sub(r'[^\w\s-]', '', raw).strip()
            cleaned = re.sub(r'\s+', ' ', cleaned)
            return cleaned or "Not available"

        except Exception as e:
            err = str(e)
            if "429" in err or "quota" in err.lower() or "rate" in err.lower():
                if attempt < max_retries - 1:
                    wait = retry_delay * (2 ** attempt)
                    print(
                        f"⏳ Rate limited. Retrying in {wait}s (attempt {attempt+1}/{max_retries})")
                    time.sleep(wait)
                    continue

            print(f"❌ AI Error: {e}")
            # Fallbacks: for experience questions return '2', otherwise a short default
            if any(w in question_name.lower() for w in ["experience", "years", "year", "how long"]):
                return "2"
            return "Not available"

    # final fallback
    if any(w in question_name.lower() for w in ["experience", "years", "year", "how long"]):
        return "2"
    return "Not available"
