from flask import Flask, request, jsonify, send_file
import instructions
import os.path

# Handling Data
import numpy as np
import scipy as sp
import pandas as pd
import PerformanceAnalysis
import pdb
from QDA import ExerciseManager

# Plotting Package
import matplotlib.pyplot as plt

# Emailing packages
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEImage import MIMEImage


app = Flask(__name__)
    
pAnalyst = PerformanceAnalysis.PerformanceAnalysis()
cols = ['pain', 'success', 'time', 'ex']



@app.route('/')
def hello():
    return 'AliviaRA!'


# Generate Plot



#### Dino Funcs ####
def check_cols(df):
    cols = df.columns.values
    for c in cols:
        if 'Unnamed' in c and c in df.columns:
            df = df.drop(c, axis=1)
        if 'pain' in c and c in df.columns:
            df = df.drop(c, axis=1)
    return df

def add_to_dbase_dino(succ, time, ex):
    if not os.path.isfile('dbase.csv'):
        dbase = pd.DataFrame()
        cols = ['success', 'time', 'ex']
        for col in cols:
            dbase[col] = [0.0]
    else:
        dbase = check_cols(pd.read_csv('dbase.csv'))
    t, s, e = list(dbase['time'].values), list(dbase['success'].values), list(dbase['ex'].values)
    dbase.ix[len(t)] = [int(succ), float(time), int(ex)]
    dbase.to_csv('dbase.csv')

def write_email(e):
    fromaddr = "aliviara420@gmail.com"
    toaddr = "tomas.vega@gmail.com"
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = "aliviara - patient update"
    with open('instructs/ex%s.txt' % (e), 'r') as myfile:
        instr=myfile.read().replace('\n', '   ')
    body = "\
    Hello: \n\n We have been recording performance on hand exercises from Chance the Rapper. The data is suggesting that their performance on some exercises is degrading, which may be early signs of Rheumatoid Arthritis. \n\n The exercises that Chance is failing to complete at the standard of healthy controls is Exercise %s. The instructions for these tasks can be viewed below and a schematic of the exercise is attached to this message. \n \
    \n \
    \n \
    %s \
    \n \
    \n \
    \n \
    Best,\n \
    The Aliviara Team \n \n \n \
    " % (e, instr) 
    msg.attach(MIMEText(body, 'plain'))
    msg.attach(MIMEImage(file("final_figs/ex%s.jpg" % (str(e))).read()))
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(fromaddr, 'password420')
    text = msg.as_string()
    server.sendmail(fromaddr, toaddr, text)
    server.quit()
    print 'email sent'


def is_consis_fail(e):
    db = check_cols(pd.read_csv('dbase.csv'))
    if float(e) not in db.ex.values:
        return False
    exer = db[db.ex == float(e)]
    if len(exer) < 3:
        return False
    succs = exer['success'].values
    last_three = [succs[-3], succs[-2], succs[-1]]
    if 1 in last_three:
        return False
    return True

# Generate Plot
def plot_prog():
    ex_map = {0: 'Make a Fist', 1: 'Finger Stretch', 2: 'Claw Stretch', \
    3: 'Grip Strength', 4: 'Index Lift', 5: 'Middle Lift', \
    6: 'Ring Lift', 7: 'Pinky Lift', 8: 'Thumb Flex', \
    9: 'Index-Thumb Touch', 10: 'Middle-Thumb Touch', 11: 'Ring-Thumb Touch', \
    12: 'Pinky-Thumb Touch'}

    calib, dbase = check_cols(pd.read_csv('dummy_calibration.csv')), check_cols(pd.read_csv('dummy_dbase.csv'))
    mu, sig = np.mean(calib['time']), np.std(calib['time'])
    thresh = mu + (2 * sig)
    f, axarr = plt.subplots(nrows=5, ncols=3)
    for ind in range(15):
        ex_dat = dbase[dbase.ex == ind]
        time_dat = ex_dat['time'].values
        mu_time = np.mean(time_dat)
        calib_time = calib[calib.ex == ind]['time']
        r, c = ind / 3, ind % 3
        if ind == 13:
            axarr[r, c].set_xlabel('Trial')
            axarr[r, c].set_xticklabels([])
            axarr[r, c-1].set_yticklabels([])
            continue
        if ind == 14:
            axarr[r, c].set_xlabel('Trial')
            axarr[r, c].set_xticklabels([])
            axarr[r, c].set_yticklabels([])
            continue
        if r == 2 and c == 0:
            axarr[r, c].set_ylabel('Time to Complete')
        if r == 4:
            axarr[r, c].set_xlabel('Trial')
        mu, sig = np.mean(calib_time), np.std(calib_time)
        thresh = mu + (2 * sig)
        if r == 4 and c == 0:
            axarr[r, c].set_xticklabels([])
            c = 1
        axarr[r, c].axhline(y=thresh,color='k',ls='dashed')
        axarr[r, c].set_title(ex_map[ind])
        axarr[r, c].plot(range(len(time_dat)), [t / mu_time for t in time_dat])
        axarr[r, c].set_xticklabels([])
        axarr[r, c].set_yticklabels([])
    f.subplots_adjust(hspace=.75)
    plt.savefig('ex_progress.jpg')
# all_dat = pd.DataFram()
# columns = 
# for col in columns:
#     dbase[col] = [0.0]


###########

def processCData(pain, fingers):
    i = 0
    data = []
    pain = int(pain)
    for measure in fingers:
        measure = str(measure).strip('[]')
        measure = [int(d) for d in measure if d != "," and d != ' ']
        measure.append(int(pain))
        data.append(measure)
        i += 1
    add_to_dbase('finger1,finger2,finger3,finger4,finger5,pain', data, 'classificationData.csv')


def add_to_dbase(columns, data, filename):
    if os.path.isfile(filename):
        f = open(filename, 'a')
    else:
        # pAnalyst.dataFile = filename
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
    fingers = params['fingers']
    time = params['time']
    success = params['success']
    pain = params['pain']
    print "Exercise: " + str(exercise)
    print "Fingers: " + str(fingers)
    print "Time: " + str(time)
    print "Success: " + str(success)
    print "Pain: " + str(pain)
    add_to_dbase_dino(success, time, exercise)
    if is_consis_fail(exercise):
        write_email(exercise)

    ###########################


 #   pAnalyst.checkOnPatient(exercise)
   # pdb.set_trace()
    processCData(pain, fingers)
    return jsonify(result={"status":200})


@app.route('/plan')
def sendExercise():
    if not trainor.ready:
        return jsonify([])
    return jsonify(result={"status": 200})


@app.route('/get_image', methods=['GET'])
def get_image():
    # if request.args.get('type') == '1':
    #    filename = 'ok.gif'
    # else:
    #    filename = 'error.gif'
    plot_prog()
    return send_file('ex_progress.jpg', mimetype='image/jpg')


if __name__ == '__main__':
    app.run()
