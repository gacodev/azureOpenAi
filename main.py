import os
import requests
from dotenv import load_dotenv
from flask import Flask, request, jsonify

load_dotenv()

app = Flask(__name__)

api_key = os.getenv("AZURE_OPENAI_API_KEY")
azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
api_version = os.getenv("AZURE_OPENAI_API_VERSION")
deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")

if not all([api_key, azure_endpoint, api_version, deployment_name]):
    raise ValueError("Missing required environment variables. Please check your .env file.")

@app.route('/chat', methods=['POST'])
def chat():
    try:
        prompt = request.json.get('prompt')
        if not prompt:
            return jsonify({"error": "No prompt provided"}), 400

        url = f"{azure_endpoint}openai/deployments/{deployment_name}/chat/completions"
        headers = {"Content-Type": "application/json", "api-key": api_key}
        payload = {
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 150
        }

        response = requests.post(url, headers=headers, json=payload, params={"api-version": api_version})
        
        if response.status_code == 200:
            result = response.json()['choices'][0]['message']['content'].strip()
            return jsonify({"response": result})
        else:
            return jsonify({"error": f"Request error: {response.status_code}"}), response.status_code

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "message": "Welcome to the Azure OpenAI API. Use /chat to interact with the model.",
        "deployment": deployment_name
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)