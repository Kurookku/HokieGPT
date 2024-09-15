from flask import Flask, request, jsonify, send_file
from openai import OpenAI
import os
import base64
import requests
from pathlib import Path
from pdf2image import convert_from_path
from dotenv import load_dotenv
from markdown_pdf import MarkdownPdf, Section


# Load environment variables from .env file
load_dotenv()

# Get the OpenAI API key
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=OPENAI_API_KEY)

# Initialize the Flask app
app = Flask(__name__)

# Function to convert images to base64
def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


# Function to convert markdown files to a single PDF
def markdown_files_to_pdf(session_id, output_pdf_path):
    print(session_id)
    pdf = MarkdownPdf(toc_level=2)  # Set TOC level (optional)
    markdown_dir = os.path.join("pdf_conversions", session_id, "adjusted_markdowns")
    
    # Iterate over each markdown file in the adjusted_markdowns folder
    for markdown_file in sorted(Path(markdown_dir).glob('*.md')):
        with open(markdown_file, 'r', encoding='utf-8') as file:
            markdown_text = file.read()
            pdf.add_section(Section(markdown_text))  # Add markdown content as a section

    # Save the PDF file
    pdf.save(output_pdf_path)

# Function to convert an image to markdown using OpenAI
def image_to_markdown(base64_image, api_key):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    payload = {
        "model": "gpt-4o-mini",
        "messages": [{
            "role": "user",
            "content": [{
                "type": "text",
                "text": "Give me the markdown text output from this page in a PDF using formatting to match the structure of the page as close as you can get. Only output the markdown and nothing else."
            }, {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}"
                }
            }]
        }],
        "max_tokens": 4096
    }
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload).json()
    
    return response['choices'][0]['message']['content']

# Function to clean markdown content based on the provided instruction
def clean_markdown_content(text, instruction):
    """
    Sends the markdown text to OpenAI to remove irrelevant content based on user instructions.
    """
    response = client.chat.completions.create(
        model="gpt-4-turbo-preview",
        messages=[
            {
                "role": "system",
                "content": f"You are tasked with cleaning up the following markdown text and applying the following instruction: {instruction}. You should return only the cleaned-up markdown text."
            },
            {
                "role": "user",
                "content": text,
            }
        ],
        max_tokens=4096
    )

    try:
        cleaned_content = response.choices[0].message.content if response.choices else ""
    except AttributeError:
        cleaned_content = "Error in processing markdown content."
    
    return cleaned_content

# Flask API endpoint to generate and download a PDF
@app.route('/download-pdf', methods=['POST'])
def download_pdf():
    print("Converting markdown to PDF for download!")
    
    # Get session_id from the form data
    session_id = request.form.get('session_id')
    print("SESSION ID: ........", session_id)
    
    # Define the input directory for adjusted markdowns and the output PDF path
    adjusted_markdown_dir = os.path.join("pdf_conversions", session_id, "adjusted_markdowns")
    output_pdf_path = os.path.join("pdf_conversions", session_id, "output.pdf")
    
    if not os.path.exists(adjusted_markdown_dir):
        return jsonify({"error": f"Adjusted markdown folder for session {session_id} not found."}), 400

    # Convert the adjusted markdown files into a single PDF
    markdown_files_to_pdf(session_id, output_pdf_path)

    print(f"Markdowns converted to PDF at {output_pdf_path}")

    # Send the PDF back to the user as a downloadable file
    return send_file(output_pdf_path, as_attachment=True, download_name=f"{session_id}_output.pdf")



# Flask API endpoint to convert a PDF to markdown and save the original PDF
@app.route('/convert-pdf', methods=['POST'])
def convert_pdf():
    print("Converting PDF to Images")
    
    # Get user_id and session_name from the form data
    user_id = request.form.get('user_id')
    session_name = request.form.get('session_name')
    pdf_file = request.files.get('pdf_file')  # Get the uploaded PDF file

    if not pdf_file:
        return jsonify({"error": "PDF file not uploaded."}), 400
    
    # Create a directory specific to the user and session
    session_dir = os.path.join("pdf_conversions", f"{session_name}")
    if not os.path.exists(session_dir):
        os.makedirs(session_dir)
    
    # Save the original PDF to the session directory
    pdf_path = os.path.join(session_dir, pdf_file.filename)
    pdf_file.save(pdf_path)

    # Convert PDF pages to images
    images_dir = os.path.join(session_dir, "images")
    if not os.path.exists(images_dir):
        os.makedirs(images_dir)
    
    images = convert_from_path(pdf_path, dpi=300, fmt='jpeg')
    total_pages = len(images)
    digits = len(str(total_pages))

    for i, image in enumerate(images):
        image_path = os.path.join(images_dir, f"Page_{str(i+1).zfill(digits)}.jpeg")
        image.save(image_path, "JPEG")
    
    # Convert images to markdown
    markdown_contents = []
    markdown_dir = os.path.join(session_dir, "markdown")
    if not os.path.exists(markdown_dir):
        os.makedirs(markdown_dir)

    for image_path in sorted(Path(images_dir).iterdir(), key=lambda x: x.stem):
        base64_image = encode_image_to_base64(str(image_path))
        markdown_content = image_to_markdown(base64_image, OPENAI_API_KEY)
        markdown_contents.append(markdown_content)

        # Save each markdown content to a file with UTF-8 encoding
        output_md_path = os.path.join(markdown_dir, f"{Path(image_path).stem}.md")
        with open(output_md_path, 'w', encoding='utf-8') as md_file:
            md_file.write(markdown_content)

    return jsonify({"markdown": markdown_contents, "directory": markdown_dir}), 200


# Flask API endpoint to clean and adjust markdown based on user instructions
@app.route('/adjust-markdown', methods=['POST'])
def adjust_markdown():
    print("Adjusting markdown!")
    
    # Get user_id, session_name, and instructions from the form data
    user_id = request.form.get('user_id')
    session_name = request.form.get('session_name')
    instruction = request.form.get('instruction', 'Clean up irrelevant text and adjust formatting.')

    print(user_id, session_name, instruction)
    
    # Define the input and output directories based on user ID and session name
    markdown_dir = os.path.join("pdf_conversions", f"{session_name}", "markdown")
    adjusted_markdown_dir = os.path.join("pdf_conversions", f"{session_name}", "adjusted_markdowns")
    
    if not os.path.exists(markdown_dir):
        return jsonify({"error": f"Markdown folder for {session_name} not found."}), 400
    
    # Create output directory for adjusted markdowns if it doesn't exist
    if not os.path.exists(adjusted_markdown_dir):
        os.makedirs(adjusted_markdown_dir)
    
    # Iterate through markdown files in the PDF markdown folder and clean/adjust content
    for markdown_file in Path(markdown_dir).glob('*.md'):
        print(f"Processing {markdown_file.name}...")
        
        with open(markdown_file, 'r', encoding='utf-8') as file:
            content = file.read()

        # Clean and adjust the markdown content based on the instruction
        cleaned_content = clean_markdown_content(content, instruction)
        
        # Save the cleaned markdown to the adjusted folder
        adjusted_md_path = os.path.join(adjusted_markdown_dir, markdown_file.name)
        with open(adjusted_md_path, 'w', encoding='utf-8') as file:
            file.write(cleaned_content)

        print(f"Cleaned markdown saved to {adjusted_md_path}")

    return jsonify({"message": f"Markdowns adjusted and saved to {adjusted_markdown_dir}."}), 200

# Run the app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
