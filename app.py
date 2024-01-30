import os
import json
from flask import Flask, request, render_template, jsonify
import vertexai
from vertexai.language_models import CodeChatModel

app = Flask(__name__)

# Configuration settings
class Config:
    GOOGLE_APPLICATION_CREDENTIALS = 'C:/loganalyzer_jan25/mlproj1-key.json'
    PROJECT_ID = "mlproj1-403203"
    LOCATION = "us-central1"
    ALLOWED_EXTENSIONS = {'txt', 'json'}
    UPLOAD_FOLDER = "C:/loganalyzer_25/temp"

# Ensure the upload folder exists
os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)

# Set the credentials environment variable
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = Config.GOOGLE_APPLICATION_CREDENTIALS

# Initialize Vertex AI with the project and location
vertexai.init(project=Config.PROJECT_ID, location=Config.LOCATION)

# Helper function to check allowed file extensions
def allowed_file(filename):
    if '.' not in filename:
        return False, "File does not have an extension."
    extension = filename.rsplit('.', 1)[1].lower()
    if extension not in Config.ALLOWED_EXTENSIONS:
        return False, f"Extension '{extension}' is not allowed."
    return True, "File is allowed."

# Helper function to analyze error logs
def analyze_error_logs(error_logs):
    analysis_results = []
    try:
        chat_model = CodeChatModel.from_pretrained("codechat-bison")
        chat = chat_model.start_chat()
        for error_log in error_logs:
            response = chat.send_message(f"analyze this -- {error_log.strip()}")
            analysis_results.append(response.text)
    except Exception as e:
        analysis_results = {"error": str(e)}
    return analysis_results

# Route to handle file uploads and analysis
@app.route("/", methods=["GET", "POST"])
def handle_main_page():
    if request.method == "GET":
        return render_template("index.html")

    if request.method == "POST":
        file = request.files.get("logFile")
        if not file:
            return jsonify({"error": "No file part in the request."}), 400

        is_allowed, message = allowed_file(file.filename)
        if not is_allowed:
            return jsonify({"error": message}), 400

        filename = file.filename
        file_path = os.path.join(Config.UPLOAD_FOLDER, filename)
        file.save(file_path)

        try:
            if filename.lower().endswith('.json'):
                with open(file_path, "r") as f:
                    data = json.load(f)
                    error_logs = data if isinstance(data, list) else data.get("logs", [])
            else:
                with open(file_path, "r") as f:
                    error_logs = f.read().splitlines()
            analysis_results = analyze_error_logs(error_logs)
            return jsonify(analysis_results)
        finally:
            os.remove(file_path)

# Run the Flask application
if __name__ == "__main__":
    app.run(debug=True)
