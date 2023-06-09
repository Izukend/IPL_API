import falcon
from wsgiref import simple_server
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from ipl_api.models import Regions, Serveurs, Cpl, Base
import json

###############
#Connexion BDD#
###############

app = application = falcon.App()
engine = create_engine("mysql+mysqlconnector://root:password@mysql/falcon_bdd", pool_size=20, pool_pre_ping=True, pool_recycle=3600,
    connect_args={"auth_plugin": "mysql_native_password"}
)
Base.metadata.create_all(bind=engine)  # Créer les tables

connexion = engine.connect()

metadata = MetaData(bind=engine)
metadata.reflect()

table = metadata.tables['cpl']

Session = sessionmaker(bind=engine)
session = Session()

class Post :
    def on_post(self, req, resp):
        try :
            data_json = json.load(req.stream)
            for data in data_json:
                data_add = Regions(uid=data['uid'], name=data['name'])
                session.add(data_add)
        except:
            pass
        print(req)
    session.commit()

class Get:

    def on_get(self, req, resp):
        # Exécuter une requête SELECT pour récupérer toutes les lignes de la table
        query = table.select()
        result = session.execute(query)

        # Convertir les résultats en une liste de dictionnaires
        rows = [dict(row) for row in result]

        # Convertir la liste de dictionnaires en JSON
        resp.body = json.dumps(rows)
        resp.status = falcon.HTTP_200

app.add_route('/', Get())
app.add_route('/', Post())

if __name__ == '__main__':
    # Démarrer l'application Falcon sur le lien http://localhost:8000/
    httpd = simple_server.make_server('localhost', 8000, app)
    httpd.serve_forever()