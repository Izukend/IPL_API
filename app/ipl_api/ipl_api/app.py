import falcon
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import Table, Column, Integer, String
import json
from ipl_api.models import Cpl, Base

app = application = falcon.App()
# Créer le moteur SQLAlchemy
engine = create_engine("mysql+mysqlconnector://root:password@mysql/falcon_bdd")
metadata = MetaData(bind=engine)
Session = sessionmaker(bind=engine)
session = Session()

#Création des tables
Base.metadata.create_all(engine)
# Définir la structure de la table
cpl = Cpl.__table__

class API:
    def __init__(self, table):
        self.post_data = []
        self.table = table

    def on_post(self, req, resp):
        try:
            data = json.loads(req.stream.read())
            data_add = Cpl(uid=data['uid'], name=data['name'])
            session.add(data_add)
            session.commit()
            resp.status = falcon.HTTP_200
            resp.body = 'Data successfully received and saved.'
        except SQLAlchemyError as e:
            session.rollback()  # Annuler les changements en cas d'erreur
            resp.status = falcon.HTTP_500
            resp.body = f'Error occurred while saving data: {str(e)}'
        except Exception as e:
            resp.status = falcon.HTTP_500
            resp.body = f'Error occurred: {str(e)}'


    def on_get(self, req, resp):
        # Exécuter une requête SELECT pour récupérer toutes les lignes de la table
        query = self.table.select()
        result = session.execute(query)

        # Convertir les résultats en une liste de dictionnaires
        rows = [dict(row) for row in result]

        # Convertir la liste de dictionnaires en JSON
        resp.body = json.dumps(rows)
        resp.status = falcon.HTTP_200

app.add_route('/api/cpl', API(cpl))
