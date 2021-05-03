from application import create_app

app = create_app()

# server only runs if this file is run directly
if __name__ == "__main__":
    # change to False during production
    app.run(debug=True)