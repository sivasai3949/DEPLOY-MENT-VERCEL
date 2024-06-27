from flask import Flask, render_template, request, session, jsonify
import openai
from dotenv import load_dotenv
import os

app = Flask(__name__)

# Load environment variables from .env file
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
app.secret_key = os.getenv("SECRET_KEY")

# Initial questions
questions = [
    "Please introduce yourself with basic background information such as where you are based, language, education.",
    "To gain further understanding, can you please describe your educational experience?",
    "What are your aspirations and higher education goals (e.g., want to study abroad or at elite universities)?",
    "Please describe if there are any financial constraints?"
]

# Options to present after initial questions
final_options = [
    "Would you like a detailed roadmap to achieve your career goals considering your academics, financial status, and study locations?",
    "Do you want personalized career guidance based on your academic performance, financial status, and desired study locations?",
    "Do you need other specific guidance like scholarship opportunities, study programs, or financial planning?",
    "Other"
]

@app.route('/')
def home():
    session.clear()
    session['question_index'] = 0
    session['user_responses'] = []
    return render_template('chat.html', initial_question=questions[0])

@app.route('/process_chat', methods=['POST'])
def process_chat():
    user_input = request.form.get('user_input')
    
    if user_input:
        question_index = session.get('question_index', 0)
        user_responses = session.get('user_responses', [])
        user_responses.append(user_input)
        session['user_responses'] = user_responses
        
        if question_index < len(questions):
            question_index += 1
            session['question_index'] = question_index
            
            if question_index < len(questions):
                return jsonify({'question': questions[question_index]})
            else:
                return jsonify({'options': final_options})
        
        else:
            try:
                bot_response = get_ai_response(user_input)
                return jsonify({'response': bot_response})
            except openai.error.RateLimitError:
                return jsonify({'error': 'Rate limit exceeded. Please try again later.'}), 429  # HTTP 429 Too Many Requests
            except openai.error.OpenAIError as e:
                app.logger.error(f"OpenAI API error: {str(e)}")
                return jsonify({'error': 'Sorry, something went wrong with the AI service. Please try again later.'}), 500
    
    return jsonify({'error': 'Invalid input'}), 400

def get_ai_response(input_text):
    messages = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]
    
    for response in session.get('user_responses', []):
        messages.append({"role": "user", "content": response})
    
    messages.append({"role": "user", "content": input_text})
    
    try:
        completion = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=messages
        )
        return completion.choices[0].message['content']
    
    except openai.error.RateLimitError as e:
        raise  # Let the Flask handler catch this and return a proper response
    except openai.error.OpenAIError as e:
        raise RuntimeError(f"Error from OpenAI API: {str(e)}")  # Propagate the error for logging and handling

if __name__ == '__main__':
    app.run(debug=True)
