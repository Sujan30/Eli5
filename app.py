import os
# Remove this line since we won't use dotenv
# from dotenv import load_dotenv
from flask import Flask, request, render_template
from openai import OpenAI
from functools import lru_cache
from dotenv import load_dotenv
import hashlib

app = Flask(__name__)

#for devlopment purposes, REMOVE BEFORE PROD
load_dotenv()

# Add this line
cached_responses = {}

conversation_history=[]

# Remove these lines since we're not using .env



# Get API key from environment variable
api_key = os.getenv("OPENAI_API_KEY")

def validate_api_key():
    if not api_key:
        return "API key not found. Please check your .env file."
    return True

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/new_search')
def new_search():
    # Clear or reinitialize the conversation history for a new thread.
    global conversation_history
    conversation_history = []
    return render_template('index.html')

@app.route('/search', methods=['POST'])
def search():
    query = request.form['query']
    validation_result = validate_api_key()
    
    if validation_result is True:
        try:
            message = prompt(query)
            #storing the conversation history both questions being asked and the responses
            conversation_history.append({'sender':'user', 'message': query})
            conversation_history.append({'sender':'eli5', 'message':message})
            

            return render_template('response.html', conversation=conversation_history)
        except Exception as e:
            return render_template('index.html', error="An error occurred while processing your request.")
    else:
        return render_template('index.html', error=validation_result)

@app.route("/continue", methods=['POST'])
def continueConvo():
    query = request.form.get('query')
    if query:
        conversation_history.append({'sender':'user', 'message':query})

        try:
            response_message = prompt(query)
            conversation_history.append({'sender':'eli5', 'message':response_message})
        except Exception as e:
            conversation_history.append({'sender':'user', 'message':'An error occured'})
        return render_template('response.html', conversation=conversation_history)

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
    formatted_prompt = """Explain this topic like I'm 5 years old, but don't address me as a 5 year old by calling me little buddy or anything similar: {query}

Please format your response using these elements:
- Use <strong> for important terms
- Use <em> for emphasis
- Use <div class="key-point"> for key takeaways
- Use <div class="example"> for examples
- Use bullet points or numbers for lists where appropriate"""

    response = client.chat.completions.create(
        model="gpt-4-turbo-preview",
        messages=[{"role": "user", "content": formatted_prompt.format(query=query)}],
        max_tokens=500

        #changed max_tokens from 1,000 to 500 to measure effiecency

        #1000 tokens = 28.8700s
        #500 tokens = 44.7100s
    )
    return response.choices[0].message.content

if __name__ == '__main__':
    app.run(debug=True) 