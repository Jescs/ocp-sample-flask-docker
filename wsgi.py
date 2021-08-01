from flask import Flask
from flask import render_template

application = Flask(__name__, instance_relative_config=True)


@application.route('/')
def index():
    return render_template("index.html")


@application.route('/pirate')
def pirate():
    return render_template("pirate.html")


@application.route('/zombie')
def zombie():
    return render_template("zombie.html")


@application.route('/legal')
def legal():
    return render_template("legal.html")


@application.route('/isready')
def isready():
    return 'isReady'


@application.route('/isalive')
def isalive():
    return 'isAlive'


if __name__ == "__main__":
    application.run()
