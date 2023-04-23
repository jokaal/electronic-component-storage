from website import create_app

# Create and run the Flask application using the Flask in-built server
# Use this for development purposes
app = create_app()
if __name__ == '__main__':
    app.run(debug=True)