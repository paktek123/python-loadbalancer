from flask import Flask, request

loadbalancer = Flask(__name__)

@loadbalancer.route('/')
def router():
    return "hello"
