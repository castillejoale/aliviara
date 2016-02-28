from flask import Flask, request, jsonify, views
from flask.ext.sqlalchemy import SQLAlchemy
from migrate.versioning import api
from config import SQLALCHEMY_DATABASE_URI
from config import SQLALCHEMY_MIGRATE_REPO

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)
from app import db, models

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
db = SQLAlchemy(app)
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

    classificationData = ReportedData(fingers, pain)
    db.session.add(classificationData)
    db.session.commit()
    performance = PerformanceData(ExerciseID, time)
    db.session.add(performance)
    db.session.commit()
    print "Exercise: " + str(exercise)
    print "Fingers: " + str(fingers)
    print "Time: " + str(time)
    print "Success: " + str(success)
    print "Pain: " + str(pain)
    return jsonify(result={"status": 200})





if __name__ == '__main__':
    app.run()
    
