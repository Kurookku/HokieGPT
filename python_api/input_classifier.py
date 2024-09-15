from flask import Flask, request, jsonify
from openai import OpenAI
import json

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the OpenAI API key
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=OPENAI_API_KEY)

app = Flask(__name__)

# Function to classify user input into one of the four categories
def classify_user_intent(description):
    # Few-shot prompting example to classify user input
    prompt = f"""
    You are an AI assistant tasked with classifying user input into one of four categories:
    
    Categories:
    1. **Adjust**: When the user wants to adjust the learning content according to their disability or preference.
    Example input: "I want to change the font size and spacing in the content to suit my needs."
    
    2. **Quiz**: When the user wants to take a quiz based on the uploaded content.
    Example input: "I want to take a quiz on the material I just uploaded."

    3. **Feedback**: When the user wants feedback on all of their quizzes.
    Example input: "Can I get feedback on how I performed on the last few quizzes?"

    4. **Others**: When the user's request doesn't fit into any of the above categories.
    Example input: "I would like to discuss a general topic not related to any content."
    
    Your task is to classify the following user input into one of these categories and provide a justification for your classification.
    
    The output should be a JSON object with the following structure:
    {{
        "classification": "<STRING>",
        "justification": "<STRING>"
    }}
    
    Now, classify the following description:
    Description: "{description}"
    """

    response = client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=[
            {"role": "system", "content": "You are an AI assistant designed to classify user input and provide justification."},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"}
    )
    
    print(response)

    # Parse the response and logprobs
    classification_response = response.choices[0].message.content.strip()
    
    try:
        classification_data = json.loads(classification_response)
    except json.JSONDecodeError:
        return {"error": "Invalid JSON response from model."}

    # Return the classification and justification
    return classification_data


# Flask route to classify user input
@app.route('/classify-intent', methods=['POST'])
def classify():
    # Get user description from the request
    data = request.get_json()
    description = data.get('description', '')

    # Classify the user's intent
    result = classify_user_intent(description)

    # Return the result as JSON
    return jsonify(result)


if __name__ == '__main__':
    app.run(port=5000, debug = True)
