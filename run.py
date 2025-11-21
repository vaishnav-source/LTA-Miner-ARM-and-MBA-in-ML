from liquor_miner import create_app

app = create_app()

if __name__ == '__main__':
    # Use 'flask run' in the terminal for the most robust execution,
    # but this direct execution is kept for convenience.
    app.run(debug=True)