from controller.app import app

def run_app():
    app.run(host='0.0.0.0', port=5000)