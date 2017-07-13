import unittest
import json
from model import db, example_data, connect_to_db
from settings import crafter


class PartyTestsDatabase(unittest.TestCase):
    """Flask tests that use the database."""

    def setUp(self):
        """Stuff to do before every test."""

        # Get the Flask test client
        self.client = app.test_client()

        # Show Flask errors that happen during tests
        app.config['TESTING'] = True

        # Connect to test database
        connect_to_db(app, "postgresql:///testydata")

        # Create tables and add sample data
        db.create_all()
        example_data()

    def tearDown(self):
        """Do at end of every test."""

        db.session.close()
        db.drop_all()

    def test_project_page(self, user_id):
        """Test projects page."""

        result = self.client.get("/user/<user_id>/projects", data=)
        self.assertEqual(result.status_code, 200)
        self.assertIn('<h1>All Projects</h1>', result.data)

   
if __name__ == '__main__':

    import unittest
    unittest.main()

     # def test_add_fav_json(self):
    #     """Test json route."""

    #     result = self.client.post("/add_fav.json", data={'photo_id': 1})
    #     response_dict = json.loads(result.data)
    #     self.assertEqual(result.status_code, 200)
    #     self.assertTrue(response_dict['success'])
    #     self.assertEqual(response_dict['photo_id'], 1)
