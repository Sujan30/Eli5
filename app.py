import os
from dotenv import load_dotenv
from flask import Flask, request, render_template
from openai import OpenAI
from functools import lru_cache
import hashlib

app = Flask(__name__)

# Add this line
cached_responses = {}

# Get the directory containing app.py
basedir = os.path.abspath(os.path.dirname(__file__))
# Load the .env file from the same directory as app.py
load_dotenv(os.path.join(basedir, '.env'))

# Get API key from environment variable
api_key = os.getenv("OPENAI_API_KEY")

def validate_api_key():
    if not api_key:
        return "API key not found. Please check your .env file."
    return True

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    query = request.form['query']
    validation_result = validate_api_key()
    
    if validation_result is True:
        try:
            message = prompt(query)
            return render_template('response.html', response=message, query=query)
        except Exception as e:
            return render_template('index.html', error="An error occurred while processing your request.")
    else:
        return render_template('index.html', error=validation_result)

@lru_cache(maxsize=100)
def get_cached_response(query_hash):
    return cached_responses.get(query_hash)

def prompt(query):
    # Create a hash of the query
    query_hash = hashlib.md5(query.encode()).hexdigest()
    
    # Check cache first
    cached_response = get_cached_response(query_hash)
    if cached_response:
        return cached_response

    client = OpenAI(api_key=api_key)
    formatted_prompt = """Explain this topic like I'm 5 years old: {query}

Please format your response using these elements:
- Use <strong> for important terms
- Use <em> for emphasis
- Use <div class="key-point"> for key takeaways
- Use <div class="example"> for examples
- Use bullet points or numbers for lists where appropriate"""

    response = client.chat.completions.create(
        model="gpt-4-turbo-preview",
        messages=[{"role": "user", "content": formatted_prompt.format(query=query)}],
        max_tokens=1000
    )
    return response.choices[0].message.content

if __name__ == '__main__':
    app.run(debug=True) 