import json
import os

with open(os.path.join(os.path.dirname(__file__), "answers.json"), "r") as f:
    EXAMPLE_ANSWERS = json.load(f)

with open(os.path.join(os.path.dirname(__file__), "answers-options.json"), "r") as f:
    EXAMPLE_ANSWER_OPTIONS = json.load(f)