import numpy as np
import pdb
import random
from scipy.io import loadmat
import math 
from decimal import *
# from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis
import csv
import pdb

class QDAClassifier:
	def __init__(self, labels, samples):
		
		self.labels = labels
		self.samples = samples
		self.means = (0,0)
		self.priors = (0,0)
		self.covars = (0,0) 
		# self.classifier = QuadraticDiscriminantAnalysis(self.priors)
		self.usedData = set()
		self.ready = False


	def computeCovariances(self, indices):
		PainSamples = []
		NoPainSamples = []

		for index in indices:
			if self.labels[index] == 1:
				NoPainSamples.append(self.samples[index])
			else:
				PainSamples.append(self.samples[index])
		covarPain = np.matrix(PainSamples).T
		covarNoPain = np.matrix(NoPainSamples).T

		return np.cov(covarPain), np.cov(covarNoPain)


	def computeMeans(self, indices):
		painCount = 0 
		painlessCount = 0
		meanPain = np.zeros(5)
		meanNoPain = np.zeros(5)
		for index in indices:
			sample = self.samples[index]
			if self.labels[index] == 0:
				meanPain += sample
				painCount += 1
			else:
				meanNoPain += sample
				painlessCount +=1
		meanPain = meanPain/painCount
		meanNoPain = meanNoPain/painlessCount

		return meanNoPain, meanPain

	def computPriors(self, indices):
		priorPain = 0
		priorNoPain = 0
		size = len(self.labels)
		for index in indices:
			label = self.labels[index]
			if label == 0:
				priorPain += 1
			else:
				priorNoPain += 1
		priorPain = float(priorPain)/float(size)
		priorNoPain = float(priorNoPain)/float(size)

		return priorPain, priorNoPain

	def generateIndices(self,  samplelength ,size=10000):
		"""
		returns a set of randomly generated indices 
		between 0 and |imgs| - 1 
		"""
		samples = [] 
		while len(samples) < samplelength:
			index = random.randrange(0, size)
			if index not in self.usedData:
				self.usedData.add(index)
				samples.append(index)
		return samples
		
	def generateSamples(self, indices):
		"""
		Given a list of indices, create a list of samples from
		self.imgData
		"""
		samples = []
		sample = None
		for index in indices:
			sample = self.samples[index]
			samples.append(sample)
		return samples

	def generateLabels(self, indices):
		"""
		Given a list of indices, create a list of labels
		from self.labels
		"""
		labels = []
		for index in indices:
			label = self.labels[index]
			labels.append(label)
		return labels

	def validate(self, indices, classifier):
		"""
		Generates validation sets and tests data.
		Uses sampledData data structure to ensure validation 
		set is disjoint from training set
		"""
		samples = self.generateSamples(indices)
		labels = self.generateLabels(indices)
		validationSize = len(samples)
		if validationSize == 0:
			pdb.set_trace()
		correct = 0 

		for i in range(len(samples)):
			sample = samples[i]
			prediction = self.predict(sample)
			label = labels[i]
			if prediction == label:
				correct += 1

		accuracy =  float(correct)/float(validationSize)
		error = 1 - accuracy
		return error, confusionMatrix

	def crossValidation(self, indices, k=10):
		"""
		Use k-fold cross validation to select the hyper parameter C
		for our SVM
		"""
		random.shuffle(indices)
		interval = len(indices)/k
		start = 0
		end = interval

		minReached = False
		bestError = float("inf")
		currError = float("inf")

		while True:
			errors = []
			i = 0
			start = 0
			end = interval
			while i < k:
				i += 1
				validationSet = indices[start:end]
				trainingSet = set(indices) - set(validationSet)
				self.posteriorCalc(trainingSet)
				error = self.predict(validationSet)
				errors.append(error)
				start = end
				end += interval 

			currError = float(reduce(lambda x, y: x + y, errors)) / float(k)
			print("This is the current error %s and c val: %f"  % (currError, hyperparam ))
			if currError < bestError:
				bestError = currError
			elif currError > bestError and currError != float("inf"):
				minReached = True 
				return hyperparam
			power += 1
			hyperparam = 2**power

	def decision(self, indices):
		self.means = self.computeMeans(indices)
		self.priors = self.computPriors(indices)
		self.covars = self.computeCovariances(indices)
		self.ready = True

	def predict(self, sample):
		if not self.ready:
			return None
		estimates = []
		for i in range(len(self.priors)):
			mean = self.means[i]
			prior = self.priors[i]
			covar = self.covars[i]
			det = np.linalg.det(covar)
			# pdb.set_trace()
			q_est = self.q_c(sample, mean, covar)
			estimate = -1/2*q_est -1/2*math.log(det) + math.log(prior)
			estimates.append(float(estimate))
		return np.argmax(estimates)

	def q_c(self,sample, mean, covar):
		invCovar = np.linalg.inv(covar)
		sample = np.asmatrix(sample).T
		mean = np.asmatrix(mean).T
		return (sample - mean).T*invCovar*(sample-mean) 





	def saveDecisionBoundary(self):
		"""
		Modify for user discrimination later
		"""
		f = open("userDistribution.csv", 'w')
		f.write('meanPain,meanNoPain,priorPain,priorNoPain\n')
		f.write(str(self.meanPain)+','+str(self.meanNoPain)+','+str(self.priorPain)+','+str(self.priorNoPain))
		np.save("userDistributionCovPain", self.covars[0])
		np.save("userDistributionCovNoPain", self.covars[1])

if __name__=='__main__':
	data =[]
	datum = [100,100,100,100,100]
	labels = np.zeros((10000,1))
	for i in range(10000):
		finger = [x*random.random() for x in datum]
		data.append(np.array(finger))
		labels[i] = 1 if random.random() < .5 else 0
	np.matrix(data)
	classy = QDAClassifier(labels, data)
	indices = classy.generateIndices(5000)
	classy.decision(indices)
	classy.predict([1,2,3,5,4])


			



