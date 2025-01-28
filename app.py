import os
from dotenv import load_dotenv
import openai
from flask import Flask, request, render_template
import os
from openai import OpenAI

app = Flask(__name__)

load_dotenv()

api_key = os.getenv("api_key")  # Make sure this matches exactly with your .env file
    

def validate_api_key():
    if not api_key:
        return "API key not found. Please check your .env file and its key name."
    return True




@app.route('/')
def home():
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    query = request.form['query']
    if validate_api_key():
        message = prompt(query)
        #change to a new page with the message
        return render_template('response.html', response=message) 
        
        
    else:
        return render_template('index.html', response="API key not found. Please check your .env file and its key name.")

@app.route('/ask-another', methods=['POST'])
def ask_another():
    return render_template('index.html')

def prompt(query):
    if not api_key:
        return "API key not found. Please check your .env file and its key name."
    
    client = OpenAI(api_key=api_key)
    formatted_prompt = """Explain this topic like I'm 5 years old: {query}

Please format your response using these elements:
- Use <strong> for important terms
- Use <em> for emphasis
- Use <div class="key-point"> for key takeaways
- Use <div class="example"> for examples
- Use bullet points or numbers for lists where appropriate"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        store=True,
        messages=[{"role": "user", "content": formatted_prompt.format(query=query)}],
        max_tokens=1000
    )
    return response.choices[0].message.content

if __name__ == '__main__':
    # Move index.html to templates folder
    os.makedirs('templates', exist_ok=True)
    if os.path.exists('index.html'):
        os.rename('index.html', 'templates/index.html')
    
    app.run(debug=True) 