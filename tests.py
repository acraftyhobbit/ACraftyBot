import unittest
import json
from lib.model import db, example_data, connect_to_db, Project
from settings import crafter
from server import app
from lib.utilities import add_user, add_project
from datetime import datetime
USER_ID = 123
PROJECT_NAME = "this is a test"
TIME = datetime.now()


class TestRoutes(unittest.TestCase):
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

        # Create test objects
        user = add_user(USER_ID)
        project = add_project(sender_id=USER_ID, name=PROJECT_NAME)

    def tearDown(self):
        """Do at end of every test."""

        db.session.close()
        db.drop_all()

    def test_all_projects_page(self):
        """Test projects page."""
        result = self.client.get("/user/{}/projects".format(USER_ID))
        self.assertEqual(result.status_code, 200)
        self.assertIn('<h1>All Projects</h1>', result.data)

    def test_incomplete_project_page(self):
        """Test project details page."""
        result = self.client.get("/user/{}/projects/{}".format(USER_ID, 1))
        self.assertEqual(result.status_code, 404)

class TestNewProjectPath(unittest.TestCase):
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

        message = {"object":"page","entry":[{"id":"526643294144028","time":1500140277687,"messaging":[{"sender":{"id":"1397850150328689"},"recipient":{"id":"526643294144028"},"timestamp":1500140277515,"message":{"mid":"mid.$cAAHe-rrZ_CBjeJlXC1dR1QSV7ptV","seq":106944,"text":"craftybot"}}]}]}
        result = self.client.post("/webhook", data=json.dumps(message))
        message = {"object":"page","entry":[{"id":"526643294144028","time":1500140901520,"messaging":[{"sender":{"id":"1397850150328689"},"recipient":{"id":"526643294144028"},"timestamp":1500140901360,"message":{"quick_reply":{"payload":"NEW_PROJECT"},"mid":"mid.$cAAHe-rrZ_CBjeKLb8FdR12XQyKr5","seq":106950,"text":"New Project"}}]}]}
        result = self.client.post("/webhook", data=json.dumps(message))
        message = {"object":"page","entry":[{"id":"526643294144028","time":1500140911420,"messaging":[{"sender":{"id":"1397850150328689"},"recipient":{"id":"526643294144028"},"timestamp":1500140911261,"message":{"mid":"mid.$cAAHe-rrZ_CBjeKMCnVdR129475J0","seq":106954,"text":"testing"}}]}]}
        result = self.client.post("/webhook", data=json.dumps(message))
        message = {"object":"page","entry":[{"id":"526643294144028","time":1500140930743,"messaging":[{"sender":{"id":"1397850150328689"},"recipient":{"id":"526643294144028"},"timestamp":1500140930597,"message":{"mid":"mid.$cAAHe-rrZ_CBjeKNOJVdR14DeIjdS","seq":106958,"attachments":[{"type":"image","payload":{"url":"https:\/\/scontent.xx.fbcdn.net\/v\/t34.0-12\/20136727_595372423179_699581314_n.jpg?_nc_ad=z-m&oh=c3a5fd1f813c3dbfefb85ed9445d23bc&oe=596D27DC"}}]}}]}]}
        result = self.client.post("/webhook", data=json.dumps(message))
        message = {"object":"page","entry":[{"id":"526643294144028","time":1500140946943,"messaging":[{"sender":{"id":"1397850150328689"},"recipient":{"id":"526643294144028"},"timestamp":1500140946800,"message":{"mid":"mid.$cAAHe-rrZ_CBjeKONcFdR1481WVp7","seq":106962,"attachments":[{"type":"image","payload":{"url":"https:\/\/scontent.xx.fbcdn.net\/v\/t35.0-12\/20107917_595372428169_519052794_o.jpg?_nc_ad=z-m&oh=90fc24658b2e6d90c82ecf126c898d93&oe=596D1704"}}]}}]}]}
        result = self.client.post("/webhook", data=json.dumps(message))
        message = {"object":"page","entry":[{"id":"526643294144028","time":1500140953734,"messaging":[{"sender":{"id":"1397850150328689"},"recipient":{"id":"526643294144028"},"timestamp":1500140953564,"message":{"mid":"mid.$cAAHe-rrZ_CBjeKOn3FdR15jLyyrE","seq":106966,"text":"4"}}]}]}
        result = self.client.post("/webhook", data=json.dumps(message))
        message = {"object":"page","entry":[{"id":"526643294144028","time":1500140961964,"messaging":[{"sender":{"id":"1397850150328689"},"recipient":{"id":"526643294144028"},"timestamp":1500140961808,"message":{"quick_reply":{"payload":"NOTE"},"mid":"mid.$cAAHe-rrZ_CBjeKPIEFdR16DW6KQm","seq":106969,"text":"Note"}}]}]}
        result = self.client.post("/webhook", data=json.dumps(message))
        message = {"object":"page","entry":[{"id":"526643294144028","time":1500140973805,"messaging":[{"sender":{"id":"1397850150328689"},"recipient":{"id":"526643294144028"},"timestamp":1500140973628,"message":{"mid":"mid.$cAAHe-rrZ_CBjeKP2PFdR16xkLuVE","seq":106974,"text":"finished test!!!"}}]}]}
        result = self.client.post("/webhook", data=json.dumps(message))


    def tearDown(self):
        """Do at end of every test."""

        db.session.close()
        db.drop_all()

    def test_project_exists(self):
        project = Project.query.filter(Project.user_id == 1397850150328689, Project.name == 'testing').first()
        self.assertIsNotNone(project)
        self.assertIsNotNone(project.fabric_id)
        self.assertIsNotNone(project.pattern_id)
        self.assertIsNotNone(project.due_at)
        self.assertEqual(project.notes, 'finished test!!!')


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
