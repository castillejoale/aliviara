import numpy as np
import pdb
import random
from scipy.io import loadmat
import math 
from decimal import *
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis
import csv
import pdb

class QDAClassifier:
	def __init__(self, data):
		self.data = data
		self.labesl = labels
		self.samples = samples
		self.meanNoPain, self.meanPain = self.computeMeans()
		self.priors, self.priorNoPain = self.computPriors()
		self.classifier = QuadraticDiscriminantAnalysis(self.priors)




	def computeMeans(self):
		painCount = 0 
		painlessCount = 0
		meanPain = np.zeros(5)
		meanNoPain = np.zeros(5)
		for i in range(len(self.samples))
			if self.labels[i] == 0:
				meanPain += sample
				painCount += 1
			else:
				meanNoPain += sample
				painlessCount +=1
		meanPain = meanPain/painCount
		meanNoPain = meanNoPain/painlessCount

		return meanNoPain, meanPain

	def computPriors(self):
		priorPain = 0
		priorNoPain = 0
		size = len(self.labels)
		for label in self.labels:
			if label == 0:
				priorPain += 1
			else:
				priorNoPain += 1
		priorPain = priorPain/size
		priorNoPain = priorNoPain/size

		return priorPain, priorNoPain

	def fitData(self):
		self.classifier.fit(self.samples, self.labels)

	def predict(self, data):
		return self.classifier.predict(data)

			



