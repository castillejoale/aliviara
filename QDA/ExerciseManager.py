import numpy as np
import pdb
import random
from scipy.io import loadmat
import math 
from decimal import *
import csv
import pdb
import QDA
import csv


class ExerciseManager():

    def __init__(self, exercises, trainingData):
        self.exercises = exercises
        self.trainingData = trainingData

        if self.trainingData != None:
            self.ready = True
            labels, samples = self.handleData(self.trainingData)
        else:
            self.ready = False
            labels = None
            samples = None
        self.QDA = QDAClassifier(labels, samples)
        self.meanPain, self.meanNoPain = self.QDA.computeMeans()


    def handleData(self, trainingCSV):
        samples = []
        labels = []
        f = open(trainingCSV, 'r')
        reader = csv.reader(trainingCSV, delimiter=',', quotechar='|')
        for row in reader:
            numRow = [int(x) for x in row if x!=',' and x != ' ']
            labels.append(numRow[5])
            samples.append(numRow[0:5])
        return labels, samples

    def createProgram(self, amtExercise, intensityLvl = 0):
		program = []
		size = len(self.exercises)
		p = intensityLvl*.25
		while len(program) < amtExercise:
			index = random.randrange(0, size)
			exercise = self.exercises[exercise]
			rating = self.QDA.predict(exercise)
			if rating == 1:
				program.append((0, index))
			else:
				flip = biasedFlip(p)
				if flip:

					program.append[(1, index)]
		return program



    def biasedFlip(p):
		return True if random.random() < p else False
    def fitData(self):
        if self.ready:
            indices = self.QDA.generateIndices(90,100)
            self.QDA.decision(indices)
            
