import json
import os

with open(os.path.join(os.path.dirname(__file__), "answers.json"), "r") as f:
    EXAMPLE_ANSWERS = json.load(f)