class ReportedData(db.Model):
    id = db.Column(db.Integer, primary=True)
    finger1 = db.Column(db.Integer, unique=True)
    finger2 = db.Column(db.Integer, unique=True)
    finger3 = db.Column(db.Integer, unique=True)
    finger4 = db.Column(db.Integer, unique=True)
    finger4 = db.Column(db.Integer, unique=True)
    finger5 = db.Column(db.Integer, unique=True)
    Pain = db.Column(db.Integer, unique=True)

    def __init__(self, fingers, pain):
        self.finger1 = fingers[0]
        self.finger2 = fingers[1]
        self.finger3 = fingers[2]
        self.finger4 = fingers[3]
        self.finger5 = fingers[4]
        self.pain = pain

class PerformanceData(db.Model):
    id = db.Column(db.Integer, primary=True)
    ExerciseID = db.Column(db.String(80), unique=True)
    time = db.Column(db.Integer, unique=True)

    def __init__(self, ExerciseID, time ):
        self.ExerciseID = ExerciseID
        self.time = time


class ExerciseData(db.Model):
    id = db.Column(db.Integer, primary=True)
    ExerciseID = db.Column(db.Integer, unique=True)
    finger1 = db.Column(db.Integer, unique=True)
    finger2 = db.Column(db.Integer, unique=True)
    finger3 = db.Column(db.Integer, unique=True)
    finger4 = db.Column(db.Integer, unique=True)
    finger4 = db.Column(db.Integer, unique=True)
    finger5 = db.Column(db.Integer, unique=True)

    def __init__(self, ExerciseID,fingers):
        self.ExerciseID = ExerciseID
        self.finger1 = fingers[0]
        self.finger2 = fingers[1]
        self.finger3 = fingers[2]
        self.finger4 = fingers[3]
        self.finger5 = fingers[4]

