from flask import Flask
from flask_mysqldb import MySQL
import MySQLdb.cursors

mysql = MySQL()
def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'thisisarandomsecretkey1111' #encrypts the cookies and session data related to website (dont worry bout it)
    
   
    app.config['MYSQL_HOST'] = "localhost"
    app.config['MYSQL_USER'] = "root"
    app.config['MYSQL_PASSWORD'] = "root"
    app.config['MYSQL_DB'] = "fssis"

    mysql.init_app(app)

    from .routes import routes
    from .controller import controller

    app.register_blueprint(routes, url_prefix = '/')
    app.register_blueprint(controller, url_prefix='/')



    return app