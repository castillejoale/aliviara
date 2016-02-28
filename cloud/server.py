from flask import Flask, request, jsonify, send_file
import instructions
import os.path

# Handling Data
import numpy as np
import scipy as sp
import pandas as pd


import pdb


app = Flask(__name__)
pAnalyst = PerformanceAnalysis()
cols = ['pain', 'success', 'time', 'ex']



@app.route('/')
def hello():
    return 'AliviaRA!'


# Generate Plot




# all_dat = pd.DataFram()
# columns = 
# for col in columns:
#     dbase[col] = [0.0]

def add_to_all(pain, fing, ex, succ):
    return False

def processCData(pain, fingers):
    i = 0
    data = []
    pain = [int(d) for d in str(pain).strip('[]') if d != "," and d != ' ']
    for measure in fingers:
        measure = str(measure).strip('[]')
        measure = [int(d) for d in measure if d != "," and d != ' ']
        measure.append(int(pain[i]))
        data.append(measure)
        i += 1
    add_to_dbase('finger1,finger2,finger3,finger4,finger5,pain' ,data, 'classificationData.csv')




def add_to_dbase(columns, data, filename):
    if os.path.isfile(filename):
        f = open(filename, 'a')
    else:
        pAnalyst.dataFile = filename
        f = open(filename, 'w')
        f.write(columns+"\n")
    for datum in data:
        row = [int(d) for d in datum]
        row = str(row).strip('[]') + "\n"
        f.write(row)


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
    print 'about to add'
    add_to_dbase("success,time,exercise",[[success, time, exercise]], 'performanceStats.csv')
    pAnalyst.checkOnPatient(exercise)
    pdb.set_trace()
    prog()
    processCData(pain, fingers)

# @app.route('/designExercise', methods=['POST']):
# def sendExercise()



    return jsonify(result={"status": 200})


@app.route('/get_image')
def get_image():
    # if request.args.get('type') == '1':
    #    filename = 'ok.gif'
    # else:
    #    filename = 'error.gif'
    pAnalyst.plot_prog()
    return send_file('ex_progress.jpg', mimetype='image/jpg')


if __name__ == '__main__':
    app.run()
    
