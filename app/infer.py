from difflib import get_close_matches
from .answers import EXAMPLE_ANSWERS
from .openai_helper import generate_response
from .gemini import bard_flash_response


def infer_answer(question_name: str, options=None) -> str:
    match = get_close_matches(
        question_name, EXAMPLE_ANSWERS.keys(), n=1, cutoff=0.6)

    if match:
        if options:
            # Try matching EXAMPLE_ANSWERS[match[0]] to options
            example_answer = EXAMPLE_ANSWERS[match[0]]
            opt = get_close_matches(example_answer, options, n=1, cutoff=0.6)
            return opt[0] if opt else options[0]
        return EXAMPLE_ANSWERS[match[0]]

    print("💬 Asking OpenAI for answer:", question_name)
    with open("answers.txt", "w") as f:
        f.write(question_name + "\t")
        if options:
            f.write("Options: " + ", ".join(options) + "\t")
        f.write("\n")
    try:
        print("🔗 Using OpenAI to infer answer...")
        # return generate_response(question_name, options)
        return bard_flash_response(f"{question_name} \nOptions: {options}") if options else bard_flash_response(question_name)
    except Exception as e:
        print(f"⚠️ OpenAI fallback failed: {e}")
        return options[0] if options else "Yes"
