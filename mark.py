from MarkAdmin import *
from MarkFlask import *

app = None
import logging
from logging.handlers import TimedRotatingFileHandler


def main(p=80):
    port = os.getenv('FLASK_PORT', str(p))
    addr = os.getenv('FLASK_ADDR', '0.0.0.0')
    logpath = os.getenv('DB_PATH', "./db/")
    logpath += 'web.log'
    """"""
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    handler = TimedRotatingFileHandler(filename=logpath,
                                       when="w0",
                                       backupCount=5)
    logger.handlers = []
    logger.addHandler(handler)

    global app
    app = CreateWallApp()

    with app.app_context():
        db = CreateWallDatabase(app)
        CreateWallAdmin(app, db)
        app.run(host=addr, port=int(port), debug=False, threaded=True)


main(5002)
