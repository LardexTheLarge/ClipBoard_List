from flask import Flask, request, jsonify
import os

app = Flask(__name__)

# Directory to store notes
NOTES_DIR = "notes"
if not os.path.exists(NOTES_DIR):
    os.makedirs(NOTES_DIR)

@app.route("/notes", methods=["GET"])
def get_notes():
    """Returns a list of all notes."""
    notes = [f.replace(".txt", "") for f in os.listdir(NOTES_DIR) if f.endswith(".txt")]
    return jsonify(notes)

@app.route("/notes/<title>", methods=["GET"])
def get_note(title):
    """Returns the content of a specific note."""
    try:
        with open(f"{NOTES_DIR}/{title}.txt", "r") as file:
            content = file.read()
        return jsonify({"title": title, "content": content})
    except FileNotFoundError:
        return jsonify({"error": "Note not found"}), 404

@app.route("/notes", methods=["POST"])
def save_note():
    """Saves a new note."""
    data = request.json
    title = data.get("title")
    content = data.get("content")

    if not title or not content:
        return jsonify({"error": "Title and content are required"}), 400

    with open(f"{NOTES_DIR}/{title}.txt", "w") as file:
        file.write(content)

    return jsonify({"message": "Note saved successfully"})

@app.route("/notes/<title>", methods=["DELETE"])
def delete_note(title):
    """Deletes a specific note."""
    try:
        os.remove(f"{NOTES_DIR}/{title}.txt")
        return jsonify({"message": f"Note '{title}' deleted successfully"})
    except FileNotFoundError:
        return jsonify({"error": "Note not found"}), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)