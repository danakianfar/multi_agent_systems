from flask import Flask
app = Flask('pure_ai_no_ethics')

@app.route("/netlogo")
def hello():
    return "(1, 2, 3)"

if __name__ == "__main__":
    app.run()