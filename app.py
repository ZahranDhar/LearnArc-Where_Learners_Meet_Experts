from flask import Flask, request, render_template
import os

app = Flask(__name__)

# Folder to save uploaded images
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Handle Open Website Request
@app.route('/')
def form():
    return render_template('login.html')

# Handle Signup Request 
@app.route('/signUp', methods=['POST'])
def signUp():
    name = request.form['name']
    username = request.form['username']
    password = request.form['password']
    age = request.form['age']
    
    profilePicture = request.files['profilepicture']
    if profilePicture:
        file_path = os.path.join(UPLOAD_FOLDER, profilePicture.filename)
        profilePicture.save(file_path)
    
    return render_template('Home.html')

if __name__ == '__main__':
    app.run(debug=True)
