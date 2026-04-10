#-------------------------------------------------------------------------------------------------
# File: run.py
# Purpose: Entry point for running the Flask application. It imports the create_app function from the app package, creates an instance of the Flask application, and runs it.
# Prompt: What is the best way to layout all the directories for flask and pythonanywhere
# This file serves as the main entry point for the Flask application. 
# It imports the create_app function from the app package, creates an instance of the Flask application, and runs it.
from app import create_app

# Create the application instance
app = create_app()

if __name__ == "__main__":
    # Local development runner
    app.run(debug=True, port=5000)