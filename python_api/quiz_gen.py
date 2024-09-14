from flask import Flask, request, jsonify
from openai import OpenAI
import os
from pathlib import Path
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the OpenAI API key
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=OPENAI_API_KEY)

app = Flask(__name__)

# Function to read a maximum of 20 markdown files from the provided directory
def compile_markdown_content(directory_path, max_files=20):
    markdown_content = ""

    # Get the first `max_files` markdown files
    md_files = sorted(Path(directory_path).glob('*.md'))[:max_files]

    # Read each file and compile content
    for md_file in md_files:
        with open(md_file, 'r', encoding='utf-8') as file:
            content = file.read()
            markdown_content += content + "\n\n"  # Append content with spacing

    return markdown_content

# Function to generate quiz from markdown content using GPT
def generate_quiz_from_markdown(markdown_content):
    prompt = f"""
    Based on the following markdown content, generate a 10-question multiple-choice quiz. Each question should have 4 answer choices and the correct answer specified. Format the output strictly as a JSON object in the following structure:
    
    {{
        "question_1": {{
            "question": "<string>",
            "answer1": "<string>",
            "answer2": "<string>",
            "answer3": "<string>",
            "answer4": "<string>",
            "correct_answer": "<string>"
        }},
        "question_2": {{
            "question": "<string>",
            "answer1": "<string>",
            "answer2": "<string>",
            "answer3": "<string>",
            "answer4": "<string>",
            "correct_answer": "<string>"
        }},
        ...
        "question_10": {{
            "question": "<string>",
            "answer1": "<string>",
            "answer2": "<string>",
            "answer3": "<string>",
            "answer4": "<string>",
            "correct_answer": "<string>"
        }}
    }}

    Markdown Content:
    {markdown_content}
    """

    # Send the request to OpenAI API
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an AI designed to generate quizzes based on content."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=2000
    )

    # Extract quiz content from the response
    quiz_content = response.choices[0].message.content
    return quiz_content

# Flask API endpoint to generate quiz from markdown files
@app.route('/generate-quiz', methods=['POST'])
def generate_quiz():
    # Get the PDF name from the request
    data = request.get_json()
    pdf_name = data.get('pdf_name')

    # Directory path for markdown files based on the provided PDF name
    markdown_directory = f'./pdf_conversions/{pdf_name}/adjusted_markdowns'

    if not os.path.exists(markdown_directory):
        return jsonify({"error": "Markdown directory not found."}), 400

    # Compile all markdown content from the directory
    compiled_content = compile_markdown_content(markdown_directory)

    # Generate the quiz based on the compiled markdown content
    quiz_json = generate_quiz_from_markdown(compiled_content)

    # Return the generated quiz as a JSON response
    return jsonify({"quiz": quiz_json}), 200

# Run the app
if __name__ == '__main__':
    app.run(port=5003)
