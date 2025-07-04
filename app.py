from flask import Flask, request, jsonify
from flask_cors import CORS
from rag_module import get_context_from_query
from llm_module import get_llm_response
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend integration

# Add a route to serve the UI
@app.route('/')
def home():
    """Serve the chatbot UI"""
    ui_file = 'index.html'
    if os.path.exists(ui_file):
        with open(ui_file, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        return """
        <h1>🌾 Crop Recommendation API</h1>
        <p>The chatbot UI (index.html) was not found.</p>
        <p>Available endpoints:</p>
        <ul>
            <li><code>POST /chat</code> - Send queries to the chatbot</li>
            <li><code>GET /health</code> - Check API health</li>
        </ul>
        """

@app.route('/chat', methods=['POST'])
def chat():
    try:
        # Validate request
        if not request.json:
            return jsonify({"error": "Request must be JSON"}), 400
            
        user_query = request.json.get("query")
        if not user_query:
            return jsonify({"error": "Query is required"}), 400
        
        if not user_query.strip():
            return jsonify({"error": "Query cannot be empty"}), 400

        logger.info(f"Processing query: {user_query}")

        # Step 1: Retrieve context from vector database
        context = get_context_from_query(user_query)
        
        if not context:
            logger.warning("No relevant context found for query")
            context = "No specific crop data found. Please provide general farming guidance."

        # Step 2: Get LLM response using context + query
        response = get_llm_response(user_query, context)

        return jsonify({
            "response": response,
            "status": "success"
        })

    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return jsonify({
            "error": "An error occurred while processing your request",
            "status": "error"
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "message": "Crop recommendation API is running"})

if __name__ == "__main__":
    print("🌾 Starting Crop Recommendation Chatbot...")
    print("📊 API will be available at: http://localhost:5000/chat")
    print("🌐 Web UI will be available at: http://localhost:5000/")
    print("🏥 Health check at: http://localhost:5000/health")
    app.run(debug=True, host='0.0.0.0', port=5000)