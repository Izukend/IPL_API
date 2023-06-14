import falcon
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import Table, Column, Integer, String
import json
from ipl_api.models import Cpl, Base, Regions



TOKEN = 'testn'

class TokenAuthMiddleware:
    def process_request(self, req, resp):
        token = req.get_header('Authorization')
        if token and token == f'Bearer {TOKEN}':
            req.context['user'] = {'username': 'izukend'}
        else:
            raise falcon.HTTPUnauthorized('Authentication required', 'Token authentication failed')
        
app = application = falcon.App(middleware=[TokenAuthMiddleware()])

# Créer le moteur SQLAlchemy et l'ajout des tables
engine = create_engine("mysql+mysqlconnector://root:password@mysql/falcon_bdd")
metadata = MetaData(bind=engine)
Session = sessionmaker(bind=engine)
session = Session()

Base.metadata.create_all(engine)

# Définir la structure de la table
cpl = Cpl.__table__

class API:
    def __init__(self, table):
        self.post_data = []
        self.table = table

    def on_post(self, req, resp):
        user = req.context['user']
        resp.body = f'Authenticated user: {user["username"]}'
        resp.status = falcon.HTTP_200
        try:
            data = json.loads(req.stream.read())
            data_add = Cpl(uid=data['uid'], name=data['name'])

            session.add(data_add)
            session.commit()

            resp.status = falcon.HTTP_200
            resp.body = 'Data successfully received and saved.'
            
        except SQLAlchemyError as e:
            session.rollback()

            resp.status = falcon.HTTP_500
            resp.body = f'Error occurred while saving data: {str(e)}'
        except Exception as e:

            resp.status = falcon.HTTP_500
            resp.body = f'Error occurred: {str(e)}'


    def on_get(self, req, resp):
        user = req.context['user']
        resp.body = f'Authenticated user: {user["username"]}'
        resp.status = falcon.HTTP_200

        query = self.table.select()
        result = session.execute(query)

        rows = [dict(row) for row in result]

        resp.body = json.dumps(rows)
        resp.status = falcon.HTTP_200

app.add_route('/', API(cpl))
