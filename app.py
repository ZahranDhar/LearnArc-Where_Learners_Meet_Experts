from flask import Flask, request, render_template
import os

app = Flask(__name__)

# Folder to save uploaded images
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def form():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    name = request.form['name']
    username = request.form['username']
    password = request.form['password']
    age = request.form['age']
    
    # Handle profile picture
    profile_pic = request.files['profilePic']
    if profile_pic:
        file_path = os.path.join(UPLOAD_FOLDER, profile_pic.filename)
        profile_pic.save(file_path)
    
    return f"""
        <h2>Form Submitted Successfully</h2>
        <p><strong>Name:</strong> {name}</p>
        <p><strong>Username:</strong> {username}</p>
        <p><strong>Age:</strong> {age}</p>
        <p><strong>Profile Picture Saved At:</strong> {file_path}</p>
    """

if __name__ == '__main__':
    app.run(debug=True)
