from flask import Flask, request
import os

app = Flask(__name__)

@app.route('/')
def sample():
    return "This is the {} application. Serving on {}. Custom Header: {}, Host Header: {}, Custom Param: {}".format(os.environ["APP"], 
                                                                                                  os.environ["ENDPOINT"],
                                                                                                  request.headers.get("MyCustomHeader", "None"),
                                                                                                  request.headers.get("Host", os.environ["ENDPOINT"]),
                                                                                                  request.args.get("MyCustomParam", "None"))

@app.route('/healthcheck')
def healthcheck():
    return "OK"

@app.route('/v1')
def v1():
    return "This is V1"

@app.route('/v2')
def v2():
    return "This is V2"

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
