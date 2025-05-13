from flask import Blueprint, render_template, request, jsonify, current_app
from flask_login import login_required, current_user
from app.forms.chatbot import ChatForm
import requests
import json
import traceback

chatbot_bp = Blueprint('chatbot', __name__)

@chatbot_bp.route('/', methods=['GET'])
def chat():
    """Render the chatbot interface."""
    form = ChatForm()
    return render_template('chatbot/chat.html', title='AI Assistant', form=form)

@chatbot_bp.route('/ask', methods=['POST'])
def ask():
    """Process a question and return AI response using OpenRouter API."""
    data = request.get_json()
    question = data.get('question', '')
    
    if not question:
        return jsonify({'response': 'Please ask a question.'})
    
    try:
        # Prepare the request to OpenRouter API
        url = f"{current_app.config['OPENROUTER_BASE_URL']}/chat/completions"
        headers = {
            "Authorization": f"Bearer {current_app.config['OPENROUTER_API_KEY']}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "deepseek/deepseek-coder",  # Using deepseek-coder model
            "messages": [
                {
                    "role": "system",
                    "content": "You are a helpful programming assistant. Provide clear, concise answers to programming questions. Include code examples when appropriate."
                },
                {
                    "role": "user",
                    "content": question
                }
            ]
        }
        
        current_app.logger.info(f"Sending request to OpenRouter: {url}")
        
        # Make the API request
        response = requests.post(url, headers=headers, json=payload)
        
        # Log the response status and content
        current_app.logger.info(f"OpenRouter API response status: {response.status_code}")
        current_app.logger.info(f"OpenRouter API response content: {response.text[:500]}...")  # Log first 500 chars
        
        # Check if the response is successful
        response.raise_for_status()
        
        response_data = response.json()
        
        # Extract the AI's response
        if 'choices' in response_data and len(response_data['choices']) > 0:
            ai_response = response_data['choices'][0]['message']['content']
            return jsonify({'response': ai_response})
        else:
            error_msg = f"Unexpected API response structure: {json.dumps(response_data)}"
            current_app.logger.error(error_msg)
            return jsonify({'response': 'Sorry, I received an unexpected response format. Please try again.'})
            
    except requests.exceptions.RequestException as e:
        error_msg = f"Request error: {str(e)}"
        current_app.logger.error(error_msg)
        if hasattr(e, 'response') and e.response is not None:
            current_app.logger.error(f"Response status: {e.response.status_code}")
            current_app.logger.error(f"Response content: {e.response.text}")
        return jsonify({'response': f'Error connecting to AI service: {str(e)}'})
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}\n{traceback.format_exc()}"
        current_app.logger.error(error_msg)
        return jsonify({'response': 'Sorry, there was an error processing your request. Please check the server logs for details.'})

@chatbot_bp.route('/test-api', methods=['GET'])
def test_api():
    """Test the OpenRouter API connection."""
    try:
        # Prepare the request to OpenRouter API
        url = f"{current_app.config['OPENROUTER_BASE_URL']}/chat/completions"
        headers = {
            "Authorization": f"Bearer {current_app.config['OPENROUTER_API_KEY']}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "openai/gpt-3.5-turbo",  # Using a simpler model for testing
            "messages": [
                {
                    "role": "user",
                    "content": "Say hello"
                }
            ]
        }
        
        # Make the API request
        response = requests.post(url, headers=headers, json=payload)
        
        # Log the response
        current_app.logger.info(f"Test API response status: {response.status_code}")
        current_app.logger.info(f"Test API response content: {response.text[:500]}...")
        
        # Return the response details
        return jsonify({
            'status': response.status_code,
            'content': response.text,
            'api_key_used': current_app.config['OPENROUTER_API_KEY'][:10] + '...',
            'url': url
        })
        
    except Exception as e:
        error_msg = f"Test API error: {str(e)}\n{traceback.format_exc()}"
        current_app.logger.error(error_msg)
        return jsonify({'error': str(e)})
