from server import app

import json
import unittest

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
        response = tester.post('/data', data=dict(
            exercise = "ex1",
            fingers = fingers_data, 
            time = 666,
            success = 1,
            pain = 1
            ), follow_redirects=True);
        self.assertEqual(response.status_code, 200)
        assert json.loads(response.data)

    def test_dbQuery(self):
        testQuery = PerformanceData.query.filter_by(ExerciseId = 'ex1').first()
        time = testQuery.time
        self.assertEqual(time, 666)

if __name__ == '__main__':
    unittest.main()
