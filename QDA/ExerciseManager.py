import numpy as np
import pdb
import random
from scipy.io import loadmat
import math 
from decimal import *
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis
import csv
import pdb


class ExerciseManager

	def __init__(self, exercises, trainingData):
		self.exercises = exercises
		self.trainingData = trainingData
		self.QDA = QDAClassifier(trainingData)
		self.meanPain, self.meanNoPain = self.QDA.computeMeans()
		self.QDA.fitData()

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


