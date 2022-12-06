from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy

from modelos import db
from vistas.tasks import VistaTasks, VistaTask, VistaFileProcessedByUser
from vistas.tasks.vistas import VistaFiles
from vistas.users import VistaLogIn, VistaSignUp 

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='postgresql://postgres:postgres@10.42.224.4:5432'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = 'frase-secreta'
app.config['PROPAGATE_EXCEPTIONS'] = True

app_context = app.app_context()
app_context.push()

#db = SQLAlchemy(app)
db.init_app(app)
db.create_all()

cors = CORS(app)

api = Api(app)

api.add_resource(VistaSignUp, '/api/auth/signup')
api.add_resource(VistaLogIn, '/api/auth/login')
api.add_resource(VistaTasks, '/api/tasks')
api.add_resource(VistaTask, '/api/tasks/<int:id>')
api.add_resource(VistaFiles, '/api/files')
api.add_resource(VistaFileProcessedByUser, '/api/files/<string:_filename>')

jwt = JWTManager(app)
