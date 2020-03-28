from flask import Flask

loadbalancer = Flask(__name__)

@loadbalancer.route('/')
def router():
    return "hello"
