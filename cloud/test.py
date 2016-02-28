from server import app

import json
import unittest
import csv
import os
import pdb

class FlaskTestCase(unittest.TestCase):

    def test_correct_response(self):
        print 'Test correct response'
        tester = app.test_client(self)
        fingers_data = [
            [0,1,2,3,4],
            [1,2,3,4,5],
            [2,3,4,5,6],
            [3,4,5,6,7]
        ]
        print fingers_data
        painTimeline = [[1,0,0,1]]
        response = tester.post('/data', data=dict(
            exercise = 0,
            fingers = fingers_data, 
            time = 666,
            success = 0,
            pain = painTimeline
            ), follow_redirects=True);
        self.assertEqual(response.status_code, 200)
        assert json.loads(response.data)
        os.remove('classificationData.csv')
    def test_Classifier_data(self):
        print 'Test for proper csv saving'
        tester = app.test_client(self)
        fingers_data = [
            [0,1,2,3,4],
            [1,2,3,4,5],
            [2,3,4,5,6],
            [3,4,5,6,7]
        ]
        painTimeline = [[1,0,0,1]]
        response = tester.post('/data', data=dict(
            exercise = 0,
            fingers = fingers_data, 
            time = 666,
            success = 0,
            pain = 1
            ), follow_redirects=True);
        f = open('classificationData.csv' ,'r')
        reader = csv.reader(f,delimiter=',', quotechar='|')
        header = reader.next()
        self.assertEqual(header[0], 'finger1')
        firstRow = reader.next()
        self.assertEqual(int(firstRow[0]), 0)
    
        self.assertEqual(int(firstRow[5]), 1)
        os.remove('classificationData.csv')
        assert json.loads(response.data)


if __name__ == '__main__':
    unittest.main()