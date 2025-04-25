from flask import Flask, request, render_template, send_file
import openai
import PyPDF2
import docx
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

def extract_text_from_pdf(file):
    reader = PyPDF2.PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

def extract_text_from_docx(file):
    doc = docx.Document(file)
    return "\n".join([p.text for p in doc.paragraphs])

def summarize_text(text):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": f"Please summarize this text:\n{text}"}],
        temperature=0.5,
        max_tokens=500
    )
    return response.choices[0].message.content.strip()

@app.route("/", methods=["GET", "POST"])
def index():
    summary = None
    filename = None
    if request.method == "POST":
        file = request.files["file"]
        filename = secure_filename(file.filename)
        ext = filename.split(".")[-1].lower()

        if ext == "pdf":
            text = extract_text_from_pdf(file)
        elif ext == "docx":
            text = extract_text_from_docx(file)
        elif ext == "txt":
            text = file.read().decode("utf-8")
        else:
            return "Unsupported file type"

        summary = summarize_text(text)

        with open(os.path.join("static", "summary.txt"), "w", encoding="utf-8") as f:
            f.write(summary)

    return render_template("index.html", summary=summary, filename="summary.txt")

@app.route("/download")
def download():
    return send_file(os.path.join("static", "summary.txt"), as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
