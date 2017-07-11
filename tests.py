"""Tests for favorites demo."""

import json
from unittest import TestCase
from server import app

class FlaskTests(TestCase):

    def setUp(self):
        """Stuff to do before every test."""

        self.client = app.test_client()
        app.config['TESTING'] = True

    def test_index(self):
        """Test index route."""

        result = self.client.get("/user/<user_id>/projects")
        self.assertEqual(result.status_code, 200)
        self.assertIn('<h1>All Projects</h1>', result.data)

    def test_add_fav_json(self):
        """Test json route."""

        result = self.client.post("/add_fav.json", data={'photo_id': 1})
        response_dict = json.loads(result.data)
        self.assertEqual(result.status_code, 200)
        self.assertTrue(response_dict['success'])
        self.assertEqual(response_dict['photo_id'], 1)

if __name__ == '__main__':

    import unittest
    unittest.main()