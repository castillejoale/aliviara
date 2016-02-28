from email.MIMEImage import MIMEImage
import instructions
import os.path

# Handling Data
import numpy as np
import scipy as sp
import pandas as pd

# Plotting Package
import matplotlib.pyplot as plt

# Emailing packages
import smtplib
from email.MIMEMultipart import MIMEMultipart


class PerformanceAnalysis:
	def __init__(self, dataFile=None):
		self.dataFile = dataFile
		self.data = None





	def check_cols(self, df):
	    cols = df.columns.values
	    for c in cols:
	        if 'Unnamed' in c and c in df.columns:
	            df = df.drop(c, axis=1)
	    return df

	def write_email(self, e):
	    fromaddr = "aliviara420@gmail.com"
	    toaddr = "leonardinodigma@gmail.com"
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

	def is_consis_fail(self, e):
		print 'ehere'
		print len(self.fileName)
		db = check_cols(pd.read_csv(self.fileName))
		print 'loaded'
		if float(e) not in db.exercise.values:
			return False
		exer = db[db.exercise == float(e)]
		if len(exer) < 3:
			return False
		succs = exer['success'].values
		last_three = [succs[-3], succs[-2], succs[-1]]
		if 1 in last_three:
			return False
		print 'askfa'
		return True

	def plot_prog(self):
	    ex_map = {0: 'Make a Fist', 1: 'Finger Stretch', 2: 'Claw Stretch', \
	    3: 'Grip Strength', 4: 'Index Lift', 5: 'Middle Lift', \
	    6: 'Ring Lift', 7: 'Pinky Lift', 8: 'Thumb Flex', \
	    9: 'Index-Thumb Touch', 10: 'Middle-Thumb Touch', 11: 'Ring-Thumb Touch', \
	    12: 'Pinky-Thumb Touch'}


	    calib, dbase = check_cols(pd.read_csv('dummy_calibration.csv')), check_cols(pd.read_csv(self.fileName))


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
	    return False


	def checkOnPatient(self ,e):
		failing = self.is_consis_fail(e)
		if failing:
			self.write_email(e)


