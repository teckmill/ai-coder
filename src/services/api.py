from flask import Flask, jsonify, request

from src.services import code_generator

code_generator = code_generator.CodeGenerator()

app = Flask(__name__)


@app.route("/generate-code", methods=["POST"])
def generate_code():
    data = request.json
    description = data.get("description", "")
    # Call the method in CodeGenerator to generate code
    generated_code = code_generator.generate_code(description)
    return jsonify({"code": generated_code})


if __name__ == "__main__":
    app.run(debug=True)
