from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/')
def hello():
    return 'AliviaRA!'

@app.route('/data', methods=['POST'])
def data():
    params = request.form
    print params.keys()
    fingers = params.getlist('fingers')
    pressure =  params['pressure']
    print fingers
    print pressure
    return jsonify(result={"status": 200})

if __name__ == '__main__':
    app.run()
