from flask import Flask, request, jsonify
import instructions

# Handling Data
import numpy as np
import scipy as sp
import pandas as pd

# Plotting Package
import matplotlib.pyplot as plt

# Emailing packages
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEImage import MIMEImage

app = Flask(__name__)

dbase = pd.DataFrame()
cols = ['pain', 'success', 'time', 'ex']
for col in cols:
    dbase[col] = [0.0]


@app.route('/')
def hello():
    return 'AliviaRA!'

def check_cols(df):
    cols = df.columns.values
    for c in cols:
        if 'Unnamed' in c and c in df.columns:
            df = df.drop(c, axis=1)
    return df

def add_to_dbase(pain, succ, time, ex):
    dbase = check_cols(pd.read_csv('dbase.csv'))
    t, s, p, e = list(dbase['time'].values), list(dbase['success'].values), list(dbase['pain'].values), list(dbase['ex'].values)
    # t.append(float(time))    
    # s.append(int(succ))
    # p.append(float(pain))
    # e.append(int(ex))
    dbase.ix[len(t)] = [int(pain), int(succ), float(time), int(ex)]
    dbase.to_csv('dbase.csv')

def write_email(e):
    fromaddr = "alivaria420@gmail.com"
    toaddr = "leonardinodigma@gmail.com"
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = "alivaria"
    print "about to open"
    with open('instructs/ex%s.txt' % (e), 'r') as myfile:
        instr=myfile.read().replace('\n', '   ')
    print "loaded: " + instr
    body = "\
    Hello: \n\n We have been recording performance on hand exercises from Chance the Rapper. The data is suggesting that their performance on some exercises is degrading, which may be early signs of Rheumatoid Arthritis. \n\n The exercises that Chance is failing to complete at the standard of healthy controls is Exercise %s. The instructions for these tasks can be viewed below. \n \
    \n \
    \n \
    %s \
    \n \
    \n \
    \n \
    Best,\n \
    The Alivaria Team \n \n \n \
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
            c = 1
        axarr[r, c].axhline(y=thresh,color='k',ls='dashed')
        axarr[r, c].set_title(ex_map[ind])
        axarr[r, c].plot(range(len(time_dat)), [t / mu_time for t in time_dat])
        axarr[r, c].set_xticklabels([])
        axarr[r, c].set_yticklabels([])
    f.subplots_adjust(hspace=.75)
    plt.savefig('ex_progress.jpg')
    return False


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
    add_to_dbase(pain, success, time, exercise)
    if is_consis_fail(exercise):
        write_email(exercise)
    # Only if 
    plot_prog()
    return jsonify(result={"status": 200})


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('uploaded_file',
                                    filename=filename))
    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file>
         <input type=submit value=Upload>
    </form>
    ''' 



if __name__ == '__main__':
    app.run()
