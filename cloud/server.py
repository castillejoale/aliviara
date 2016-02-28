from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/')
def hello():
    return 'AliviaRA!'

@app.route('/data', methods=['POST'])
def data():
    params = request.form
    exercise = params['exercise']
    fingers = params.getlist('fingers')
    time = params['time']
    success = params['success']
    pain = params['pain']
    print "Exercise: " + str(exercise)
    print "Fingers: " + str(fingers)
    print "Time: " + str(time)
    print "Success: " + str(success)
    print "Pain: " + str(pain)
    return jsonify(result={"status": 200})

if __name__ == '__main__':
    app.run()
