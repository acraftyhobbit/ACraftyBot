from lib.utilities import check_progress_status
from lib.model import connect_to_db
from server import app
# import time
# time.sleep(90)
connect_to_db(app)
check_progress_status()
