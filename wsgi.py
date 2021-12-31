from flask import Flask
from flask import render_template

application = Flask(__name__, instance_relative_config=True)


@application.route('/')
def index():
    return render_template("index.html")



if __name__ == "__main__":
    application.run()
