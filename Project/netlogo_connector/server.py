from flask import Flask
from flask import request

app = Flask('NetLogo_API')

@app.route("/tick", methods = ['POST'])
def hello():
    print(request.form)
    print(request.form['bus24'])
    print(request.form['stop'])
    return request.form['bus24']

if __name__ == "__main__":
    app.run()