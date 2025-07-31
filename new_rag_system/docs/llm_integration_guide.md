# LLM Integration Guide

## 1. Introduction
This guide provides detailed instructions on how to connect different types of Large Language Models (LLMs) to the Advanced RAG System. The application is designed to be highly flexible, allowing you to use commercial API-based models, open-source models hosted on platforms like Hugging Face, and even your own locally hosted models.

The primary method for adding a new model is through the **Admin Dashboard** under "LLM/API Configs".

---

## 2. Method 1: API-based Models (e.g., OpenAI, Anthropic)

This is the most straightforward method and is recommended for most users.

**Step 1: Get Your API Key**
-   Obtain an API key from your chosen provider (e.g., OpenAI, Anthropic, Cohere).

**Step 2: Add the API Key to Your Environment**
-   Open your `.env` file in the `new_rag_system` directory.
-   Add a new line for your API key. The name of the variable can be anything, but we recommend a descriptive name.
    ```
    OPENAI_API_KEY="your_sk-...._key_here"
    ANTHROPIC_API_KEY="your_anthropic_key_here"
    ```

**Step 3: Add the Configuration in the Admin Dashboard**
1.  Navigate to the **Admin Dashboard** and go to the "LLM/API Configs" tab.
2.  Click "Add New Configuration".
3.  Fill out the form:
    *   **Name:** A user-friendly name (e.g., "OpenAI GPT-4o").
    *   **Type:** Select `LLM`.
    *   **Model Name:** The specific model identifier used by the provider (e.g., `gpt-4o`, `claude-3-opus-20240229`).
    *   **API Key Environment Variable:** The exact name of the variable you created in your `.env` file (e.g., `OPENAI_API_KEY`).
4.  Click "Save". The model will now be available for users to select on the Query page.

---

## 3. Method 2: Self-Hosted Local Models (e.g., Ollama)

This method allows you to run open-source models on your own hardware for privacy and cost savings. We will use **Ollama** as the primary example.

**Step 1: Install and Run a Local LLM Server**
1.  **Install Ollama:** Follow the instructions on the [Ollama website](https://ollama.com/) to download and install it on your system.
2.  **Download a Model:** From your terminal, pull the model you want to use. For example, to get Llama 3:
    ```bash
    ollama pull llama3
    ```
3.  **Run the Model:** Ollama automatically runs a server in the background. You don't need to do anything else. The server will be available at `http://localhost:11434`.

**Step 2: Add the Configuration in the Admin Dashboard**
1.  Navigate to the **Admin Dashboard** and go to the "LLM/API Configs" tab.
2.  Click "Add New Configuration".
3.  Fill out the form:
    *   **Name:** A user-friendly name (e.g., "Local Llama 3").
    *   **Type:** Select `API`.
    *   **Endpoint:** The full API endpoint for the local server. For Ollama, this is typically `http://host.docker.internal:11434/api/generate` (if the app is running in Docker) or `http://localhost:11434/api/generate`.
    *   **API Key Environment Variable:** For most local models, this is not needed. You can enter `NONE`.
4.  Click "Save". The local model will now be available for users.

*Note: The same principle applies to other local serving tools like Hugging Face's Text Generation Inference (TGI). Simply find the correct API endpoint and add it to the dashboard.*

---

## 4. Method 3 (Advanced): Creating a Custom Wrapper

If you have a custom model that doesn't have a standard API, you can create a simple API wrapper for it. The wrapper must expose a POST endpoint that accepts a JSON payload like `{"prompt": "Your prompt here"}` and returns a JSON response like `{"response": "The model's answer"}`.

Here is a minimal example using **Flask**:

```python
# custom_model_wrapper.py
from flask import Flask, request, jsonify
# from your_model_library import load_my_model

app = Flask(__name__)
# my_model = load_my_model("path/to/your/model")

@app.route('/generate', methods=['POST'])
def generate():
    data = request.get_json()
    prompt = data.get('prompt')

    # In a real scenario, you would process the prompt with your model
    # response_text = my_model.generate(prompt)
    response_text = f"This is a dummy response to the prompt: {prompt}" # Placeholder

    return jsonify({"response": response_text})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
```

You can run this script and then add `http://localhost:5001/generate` as a new API endpoint in the Admin Dashboard, following the same steps as in Method 2.
