

class QDAFromSleepy(QDAClassifier):

	def __init__(self, data, labels, samples, userName='userDistributions'):
		self.data = data
		self.labels = labels
		self.samples = samples
		self.userName = userName
		self.covars = (load('userDistributions'+'CovPain'),load('userDistributions'+'CovNoPain'))
		self.priors, self.means = self.getData()
		self.classifier = QuadraticDiscriminantAnalysis(self.priors)
		self.usedData = set()
		self.ready = False

	def self.getData(self):
		fileName = self.userName
		csvfile = open('userDistribution.csv') 
		reader = csv.reader(csvfile, delimiter=',', quotechar='|')
		reader.next()
		params = [float(x) for x in reader.next()]
		priors = (param[0], param[1])
		means = (param[2],param[3])
		return priors, means