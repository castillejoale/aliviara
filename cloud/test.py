from server import app

import json
import unittest

class FlaskTestCase(unittest.TestCase):

    def test_correct_response(self):
        print 'Test correct response'
        tester = app.test_client(self)
        response = tester.post('/data', data=dict(
            fingers = [0,1,2,3,4],
            pressure = 69
            ), follow_redirects=True);
        self.assertEqual(response.status_code, 200)
        assert json.loads(response.data)

if __name__ == '__main__':
    unittest.main()
