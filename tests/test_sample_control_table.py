import unittest
import app


class TestSampleControlTable(unittest.TestCase):
    def setUp(self):
        self.app = app.app.test_client()

    def test_get(self):
        return_value = self.app.get('/api/v1/sample_controls')
        print return_value.data
        assert len(return_value.data) > 0


if __name__ == '__main__':
    unittest.main()
