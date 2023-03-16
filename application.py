from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def index():  # put application's code here
    return render_template('index.html', name=' to Law Database')


@app.route('/<string:name>')
def index_name(name):
    return render_template('index.html', name=f', {name}')


@app.route('/feedback')
def feedback():
    return render_template('feedback.html')


@app.route('/database')
def database():
    return render_template('database.html')


if __name__ == '__main__':
    app.run()
