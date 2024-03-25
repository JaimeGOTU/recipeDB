from flask import Flask
from flask_simplelogin import SimpleLogin

app = Flask(__name__)
#SimpleLogin(app)

@app.route('/')
def home():
    return "Hello, World!"

if __name__ == "__main__":
    app.run(debug=True)