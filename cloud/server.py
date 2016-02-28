from flask import Flask, request, jsonify
import pandas as pd

app = Flask(__name__)

dbase = pd.DataFrame()
cols = ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky', 'Time', 'Success', 'Pain']
for col in cols:
    dbase[col] = [0]

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
    add_to_dbase(exercise, fingers, time, success, pain)
    return jsonify(result={"status": 200})

def add_to_dbase(ex, fingers, time, success, pain):
    for ind in range(len(fingers)):
        cols[]


if __name__ == '__main__':
    app.run()
