from flask import Flask, request
import os

app = Flask(__name__)

@app.route('/')
def sample():
    return "This is the {} application. Serving on {}. Custom Header: {}, Host Header: {}".format(os.environ["APP"], 
                                                                                                  os.environ["ENDPOINT"],
                                                                                                  request.headers.get("MyCustomHeader", "None"),
                                                                                                  request.headers.get("Host", os.environ["ENDPOINT"]))

@app.route('/healthcheck')
def healthcheck():
    return "OK"

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
