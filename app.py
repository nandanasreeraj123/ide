# from flask import Flask, request, jsonify, render_template
# from flask_cors import CORS  # Import Flask-CORS
# import subprocess
# import os
# import base64
# from quickjs import Context
# import requests
# import json
# import firebase_admin
# from firebase_admin import credentials, auth

# # Initialize Flask app
# app = Flask(__name__)

# # Enable CORS for all routes
# CORS(app)  

# # Path to store code execution outputs (if needed)
# output_path = "/tmp"

# # Firebase Admin SDK initialization (Replace with your Firebase Admin SDK JSON path)
# cred = credentials.Certificate("path/to/your/firebase-adminsdk.json")
# firebase_admin.initialize_app(cred)

# @app.route("/")
# def home():
#     return "Welcome to the IDE!"

# @app.route("/ide")
# def ide():
#     """Render the IDE interface for users"""
#     token = request.args.get("token")
#     is_verified = request.args.get("isVerified", "false") == "true"
    
#     # Validate token and isVerified flag
#     if not validate_token(token, is_verified):
#         return jsonify({"error": "Invalid token or user not verified."}), 401

#     return render_template("index.html")

# @app.route("/run", methods=["POST"])
# def run_code():
#     # Extract token and isVerified from query parameters
#     token = request.args.get("token")
#     is_verified = request.args.get("isVerified", "false") == "true"

#     # Validate token and isVerified flag
#     if not validate_token(token, is_verified):
#         return jsonify({"error": "Invalid token or user not verified."}), 401

#     # Extract the code and language from the request body
#     data = request.json
#     code = data.get("code", "")
#     language = data.get("language", "python")

#     # Execute the code based on the selected language
#     try:
#         if language == "python":
#             output = run_python_code(code)
#         elif language == "dart":
#             output = run_dart_code(code)
#         elif language == "javascript":
#             output = run_javascript_code(code)
#         elif language == "c":
#             output = run_c_code(code)
#         elif language == "cpp":
#             output = run_cpp_code(code)
#         else:
#             return jsonify({"error": "Unsupported language"}), 400
        
#         return jsonify({"output": output, "error": ""})

#     except Exception as e:
#         return jsonify({"error": str(e)})


# def validate_token(encoded_token, is_verified):
#     """Decode Base64 token and validate it"""
#     try:
#         # Decode the base64 token
#         decoded_data = base64.b64decode(encoded_token).decode("utf-8")
#         token, user_verified = decoded_data.split(":")  # Split token and eligibility flag

#         # If user_verified is False, reject the request
#         if not is_verified or user_verified != "true":
#             return False

#         # Now validate the token using Firebase
#         if not validate_firebase_token(token):
#             return False

#         return True
#     except Exception as e:
#         return False

# def validate_firebase_token(token):
#     """Validate Firebase ID token"""
#     try:
#         decoded_token = auth.verify_id_token(token)
#         return True
#     except Exception as e:
#         print(f"Error verifying token: {e}")
#         return False

# def run_python_code(code):
#     """Run Python code in a subprocess and return output"""
#     process = subprocess.Popen(
#         ["python3", "-c", code],
#         stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
#     )
#     output, error = process.communicate()
#     return output if not error else error


# def run_dart_code(code):
#     """Run Dart code using JDoodle API and return the output"""
#     client_id = "your_client_id"
#     client_secret = "your_client_secret"

#     url = "https://api.jdoodle.com/v1/execute"
    
#     payload = {
#         "clientId": client_id,
#         "clientSecret": client_secret,
#         "script": code,
#         "language": "dart",
#         "versionIndex": "0"
#     }

#     headers = {"Content-Type": "application/json"}

#     try:
#         response = requests.post(url, json=payload, headers=headers)

#         if response.status_code == 200:
#             result = response.json()
#             output = result.get("output", "No output received")
#             return output
#         else:
#             return f"Error: {response.status_code}, {response.text}"

#     except Exception as e:
#         return f"An error occurred: {str(e)}"


# def run_javascript_code(js_code):
#     try:
#         ctxt = Context()

#         ctxt.eval("""
#         var consoleOutput = [];
#         var console = {
#             log: function() { 
#                 consoleOutput.push(Array.from(arguments).join(" ")); 
#             }
#         };
#         """)

#         ctxt.eval(js_code)

#         logs = ctxt.eval("consoleOutput.join('\\n')")

#         return logs
#     except Exception as e:
#         return f"Error executing JavaScript: {str(e)}"


# def run_c_code(code):
#     """Compile and run C code, return output"""
#     filename = "temp.c"
#     with open(filename, "w") as f:
#         f.write(code)

#     process = subprocess.Popen(
#         ["gcc", filename, "-o", "temp_out"],
#         stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
#     )
#     output, error = process.communicate()
#     if error:
#         return error

#     process = subprocess.Popen(
#         ["./temp_out"],
#         stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
#     )
#     output, error = process.communicate()
#     return output if not error else error

# def run_cpp_code(code):
#     """Compile and run C++ code, return output"""
#     filename = "temp.cpp"
#     with open(filename, "w") as f:
#         f.write(code)

#     process = subprocess.Popen(
#         ["g++", filename, "-o", "temp_out"],
#         stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
#     )
#     output, error = process.communicate()
#     if error:
#         return error

#     process = subprocess.Popen(
#         ["./temp_out"],
#         stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
#     )
#     output, error = process.communicate()
#     return output if not error else error

# if __name__ == "__main__":
#     app.run(debug=True)


from flask import Flask, request, jsonify, render_template, redirect, url_for
import subprocess
from quickjs import Context
import requests
import json

app = Flask(__name__)

# Store tokens in memory (can be replaced with a more persistent store like a database or Redis)
tokens_store = {}

output_path = "/tmp"

@app.route("/")
def home():
    return "Welcome to the IDE!"

@app.route("/ide")
def ide():
    """Render the IDE interface for users"""
    return render_template("index.html")

@app.route("/run", methods=["POST"])
def run_code():
    # Extract the code and language from the request body
    data = request.json
    code = data.get("code", "")
    language = data.get("language", "python")

    # Execute the code based on the selected language
    try:
        if language == "python":
            output = run_python_code(code)
        elif language == "dart":
            output = run_dart_code(code)
        elif language == "javascript":
            output = run_javascript_code(code)
        elif language == "c":
            output = run_c_code(code)
        elif language == "cpp":
            output = run_cpp_code(code)
        else:
            return jsonify({"error": "Unsupported language"}), 400
        
        return jsonify({"output": output, "error": ""})

    except Exception as e:
        return jsonify({"error": str(e)})


def run_python_code(code):
    """Run Python code in a subprocess and return output"""
    process = subprocess.Popen(
        ["python3", "-c", code],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    output, error = process.communicate()
    return output if not error else error


def run_dart_code(code):
    """Run Dart code using JDoodle API and return the output"""
    
    # JDoodle API credentials (replace these with your actual credentials)
    client_id = "80c6ca8585ae72e8eab2ab7f9fc7e1fe"  # Replace with your client ID
    client_secret = "d4a9fc6b81452b44500d5c2705f5b241254eeb290855b4b8c6929902d173da17"  # Replace with your client secret

    # JDoodle API URL
    url = "https://api.jdoodle.com/v1/execute"
    
    # Prepare the request payload
    payload = {
        "clientId": client_id,
        "clientSecret": client_secret,
        "script": code,           # The Dart code to execute
        "language": "dart",       # Language set to Dart
        "versionIndex": "0"       # Version index for Dart (you can change this depending on JDoodle API versioning)
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)

        if response.status_code == 200:
            result = response.json()
            output = result.get("output", "No output received")
            return output
        else:
            return f"Error: {response.status_code}, {response.text}"

    except Exception as e:
        return f"An error occurred: {str(e)}"



def run_javascript_code(js_code):
    try:
        ctxt = Context()

        ctxt.eval("""
        var consoleOutput = [];
        var console = {
            log: function() { 
                consoleOutput.push(Array.from(arguments).join(" ")); 
            }
        };
        """)

        ctxt.eval(js_code)

        logs = ctxt.eval("consoleOutput.join('\\n')")

        return logs
    except Exception as e:
        return f"Error executing JavaScript: {str(e)}"




    
def run_c_code(code):
    """Compile and run C code, return output"""
    filename = "temp.c"
    with open(filename, "w") as f:
        f.write(code)
    
    # Compile the C code
    process = subprocess.Popen(
        ["gcc", filename, "-o", "temp_out"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    output, error = process.communicate()
    if error:
        return error
    
    # Run the compiled C program
    process = subprocess.Popen(
        ["./temp_out"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    output, error = process.communicate()
    return output if not error else error

def run_cpp_code(code):
    """Compile and run C++ code, return output"""
    filename = "temp.cpp"
    with open(filename, "w") as f:
        f.write(code)
    
    # Compile the C++ code
    process = subprocess.Popen(
        ["g++", filename, "-o", "temp_out"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    output, error = process.communicate()
    if error:
        return error
    
    # Run the compiled C++ program
    process = subprocess.Popen(
        ["./temp_out"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    output, error = process.communicate()
    return output if not error else error


@app.route("/token")
def validate_token():
    """Validate the token sent by the external app and redirect to /ide if valid"""
    token = request.args.get("token")

    if token not in tokens_store :
        # Invalidate the token after it's used
        tokens_store[token] = True
        # Redirect to the IDE page
        return render_template('index.html', token=token)
    else:
        # Invalid or already used token
        print(tokens_store)
        return jsonify({"error": "Invalid or already used token"}), 400
        
    
    
if __name__ == "__main__":
    app.run(debug=True)
