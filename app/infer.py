from difflib import get_close_matches
from .answers import EXAMPLE_ANSWERS, EXAMPLE_ANSWER_OPTIONS
# from .openai_helper import generate_response
from .gemini import bard_flash_response


def infer_answer(question_name: str, options=None) -> str:

    # Handle option-based questions (multiple choice)
    if options:
        match = get_close_matches(
            question_name, EXAMPLE_ANSWER_OPTIONS.keys(), n=1, cutoff=0.6)
        if match:
            example_answers = EXAMPLE_ANSWER_OPTIONS[match[0]]
            # example_answers is a list; try each candidate against actual options
            if isinstance(example_answers, str):
                example_answers = [example_answers]
            for ea in example_answers:
                opt = get_close_matches(ea, options, n=1, cutoff=0.6)
                if opt:
                    return opt[0]
            # No close match found — fall through to AI instead of defaulting to options[0]

        # No example match, use AI to select from options
        print("💬 Asking AI to select from options:", question_name)
        _log_question(question_name, options)
        try:
            print("🔗 Using Gemini to infer answer from options...")
            return bard_flash_response(question_name, options)
        except Exception as e:
            print(f"⚠️ AI selection failed: {e}")
            return options[0]

    # Handle text-based questions (free form)
    else:
        match = get_close_matches(
            question_name, EXAMPLE_ANSWERS.keys(), n=1, cutoff=0.6)
        if match:
            return EXAMPLE_ANSWERS[match[0]]

        # No example match, use AI to generate answer
        print("💬 Asking AI for answer:", question_name)
        _log_question(question_name)
        try:
            print("🔗 Using Gemini to infer answer...")
            return bard_flash_response(question_name)
        except Exception as e:
            print(f"⚠️ AI generation failed: {e}")
            return "Yes"


def _log_question(question_name: str, options=None) -> None:
    """Log question to answers.txt for future reference."""
    try:
        with open("answers.txt", "a") as f:
            f.write(question_name + "\t")
            if options:
                f.write("Options: " + ", ".join(options) + "\t")
            f.write("\n")
    except FileNotFoundError:
        with open("answers.txt", "w") as f:
            f.write(question_name + "\t")
            if options:
                f.write("Options: " + ", ".join(options) + "\t")
            f.write("\n")
