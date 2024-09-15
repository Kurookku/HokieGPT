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


# Few-shot prompting example to classify learning styles
def classify_learning_style(description):
 
    # Few-shot prompt to classify learning disabilities
    prompt = f"""
    You are an AI assistant specializing in adapting educational content to accommodate various learning disabilities. Below are descriptions of common learning disabilities with example inputs. Your task is to classify the given description into one of these disabilities, provide a justification, and offer detailed instructions on how to modify the markdown content to accommodate the disability. The instructions should specify exactly what to change in the markdown code (e.g., headers, line breaks, emphasis) to make it more accessible to the person with the identified learning disability.

    The output should be a JSON object with the following structure:
    {{
        "learning_disability": "<STRING>",
        "justification": "<STRING>",
        "instruction": "<STRING>"
    }}

    Learning disabilities:

    1. **Dyslexia**: Learners who struggle with reading long paragraphs and benefit from text that is spaced out and written with simple fonts.
    Example input: "I find it difficult to read long sections of text."
    Classification: Dyslexia
    Instruction: Use a dyslexia-friendly font (such as OpenDyslexic), increase line spacing (e.g., `line-height: 1.5` in markdown), break long text into shorter paragraphs, use bullet points (`-`) to list key points, bold important text (`**bold**`), and avoid italics.

    2. **ADHD**: Learners who have difficulty focusing on tasks for long periods and benefit from frequent breaks and clear, concise content.
    Example input: "I have a hard time focusing and need frequent breaks."
    Classification: ADHD
    Instruction: Use headers (e.g., `#` for headings) to break content into smaller, digestible chunks, add bullet points or numbered lists for clarity, and insert frequent breaks (e.g., `---` for horizontal rules in markdown) to create separation between sections.

    3. **Autism Spectrum Disorder (ASD)**: Learners who prefer concrete language, consistent structure, and may need visual aids for better understanding.
    Example input: "I struggle to follow abstract concepts and need clear examples."
    Classification: ASD
    Instruction: Use consistent and simple language. Avoid metaphors. Include clear, consistent headings (e.g., `##` for subheadings) and provide images alongside text using markdown syntax (`![alt text](url)`).

    4. **Reading Comprehension Deficit**: Learners who understand individual words but struggle with understanding longer sentences or paragraphs.
    Example input: "I can read fine, but understanding longer paragraphs is hard."
    Classification: Reading Comprehension Deficit
    Instruction: Break long sentences into shorter ones. Use bullet points (`-`) to separate ideas. Provide summaries at the end of each section with markdown blockquotes (`> Summary: ...`).

    5. **Visual Impairments (Color Blindness)**: Learners who have difficulty distinguishing between certain colors and require high-contrast text with no color-dependent instructions.
    Example input: "I can't tell the difference between red and green."
    Classification: Visual Impairment (Color Blindness)
    Instruction: Ensure high contrast between text and background, e.g., use black text on a white background. Avoid color-based instructions like "click the red button". Emphasize important text with bold (`**bold**`) or underline (e.g., `<u>underline</u>`).

    6. **Slow Processing Speed**: Learners who need more time to process information and benefit from content broken into smaller, simpler steps.
    Example input: "It takes me longer to understand new information."
    Classification: Slow Processing Speed
    Instruction: Use numbered lists (`1.`) for step-by-step instructions. Each step should contain only one action. Include summaries at the end of sections in blockquote markdown (`> Summary: ...`).

    7. **Dysgraphia**: Learners who struggle with handwriting or typing, benefiting from clear formatting and structured content.
    Example input: "I have trouble writing and organizing my thoughts."
    Classification: Dysgraphia
    Instruction: Use bullet points or numbered lists to organize ideas. Avoid long blocks of text. Use examples in blockquotes (e.g., `> Example: ...`). Provide downloadable forms or templates when possible.

    8. **Language Processing Disorder**: Learners who may struggle with understanding spoken or written language, benefiting from simplified language and additional explanations.
    Example input: "I have trouble understanding complex words."
    Classification: Language Processing Disorder
    Instruction: Use simple language and avoid jargon. Define complex terms in-line using markdown definitions (e.g., `**Word**: Definition`).

    9. **Specific Language Impairment (SLI)**: Learners who struggle with grammar and sentence structure, benefiting from simplified and color-coded grammar instructions.
    Example input: "I find grammar and sentence structure confusing."
    Classification: Specific Language Impairment (SLI)
    Instruction: Provide simplified sentence structures, color-coded or clearly separated grammar explanations (e.g., using markdown code blocks for examples).

    10. **Nonverbal Learning Disability (NLD)**: Learners who struggle with abstract thinking and prefer concrete examples and structured content.
    Example input: "I have trouble understanding abstract ideas."
    Classification: Nonverbal Learning Disability (NLD)
    Instruction: Provide concrete examples for abstract concepts, using markdown blockquotes (`> Example: ...`). Organize content with clear headings (e.g., `#`, `##`).

    If the description does not match any of the listed learning disabilities, classify it as "Unidentified Learning Disability" and provide markdown-based instructions based on the user input.
    
    Now, classify the following description, provide a justification, and give detailed markdown instructions for accommodation:
    Description: "{description}"
    """

    response = client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=[
            {"role": "system", "content": "You are an AI assistant designed to output JSON with the required fields."},
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

    # Return classification, justification, and probability of the "answer" token
    return classification_data

# Flask route to classify learning style
@app.route('/learning-style', methods=['POST'])
def classify():
    # Get user description from the request
    data = request.get_json()
    description = data.get('description', '')

    # Classify learning style
    result = classify_learning_style(description)

    # Return the result as JSON
    return jsonify(result)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002, debug = True)
