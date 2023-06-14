import falcon
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import Table, Column, Integer, String
import json
from ipl_api.models import Cpl, Base, Serveurs

# Définition du token d'authentification
TOKEN = 'testn'

class TokenAuthMiddleware:
    def process_request(self, req, resp):
        # Vérifier si le token d'authentification est présent dans l'en-tête
        token = req.get_header('Authorization')
        if token and token == f'Bearer {TOKEN}':
            # Authentification réussie, ajouter l'utilisateur au contexte de la requête
            req.context['user'] = {'username': 'tom'}
        else:
            # Authentification échouée, renvoyer une erreur 401 Unauthorized
            raise falcon.HTTPUnauthorized('Authentication required', 'Token authentication failed')

# Création de l'application Falcon avec le middleware d'authentification
app = application = falcon.App(middleware=[TokenAuthMiddleware()])

# Création du moteur SQLAlchemy et ajout des tables
engine = create_engine("mysql+mysqlconnector://root:password@mysql/falcon_bdd")
metadata = MetaData(bind=engine)
Session = sessionmaker(bind=engine)
session = Session()

Base.metadata.create_all(engine)

# Définition de la structure des tables
cpl = Cpl.__table__
srv = Serveurs.__table__

class APICPL:
    def __init__(self, table):
        self.post_data = []
        self.table = table

    def on_post(self, req, resp):
        # Récupérer l'utilisateur authentifié à partir du contexte de la requête
        user = req.context['user']
        resp.body = f'Authenticated user: {user["username"]}'
        resp.status = falcon.HTTP_200
        try:
            # Récupérer les données JSON de la requête
            data = json.loads(req.stream.read())
            data_add = Cpl(uid=data['uid'], name=data['name'])

            # Ajouter les données à la session SQLAlchemy et les sauvegarder dans la base de données
            session.add(data_add)
            session.commit()

            resp.status = falcon.HTTP_200
            resp.body = 'Data successfully received and saved.'
            
        except SQLAlchemyError as e:
            # En cas d'erreur SQLAlchemy, effectuer un rollback de la session
            session.rollback()

            resp.status = falcon.HTTP_500
            resp.body = f'Error occurred while saving data: {str(e)}'
        except Exception as e:
            # En cas d'erreur non SQLAlchemy, renvoyer une erreur 500 Internal Server Error
            resp.status = falcon.HTTP_500
            resp.body = f'Error occurred: {str(e)}'

    def on_get(self, req, resp):
        # Récupérer l'utilisateur authentifié à partir du contexte de la requête
        user = req.context['user']
        resp.body = f'Authenticated user: {user["username"]}'
        resp.status = falcon.HTTP_200

        # Exécuter une requête SQLAlchemy pour récupérer les données de la table correspondante
        query = self.table.select()
        result = session.execute(query)

        # Convertir les lignes de résultat en une liste de dictionnaires
        rows = [dict(row) for row in result]

        # Renvoyer les données sous forme de JSON dans le corps de la réponse
        resp.body = json.dumps(rows)
        resp.status = falcon.HTTP_200

class APIServeurs:
    def __init__(self, table):
        self.post_data = []
        self.table = table

    def on_post(self, req, resp):
        try:
            # Récupérer les données JSON de la requête
            data = json.loads(req.stream.read())
            # Récupérer la valeur de l'en-tête X-Forwarded-For
            x_forwarded_for = req.headers.get('X-Forwarded-For')
            if x_forwarded_for:
            # La valeur de X-Forwarded-For est présente, extraire la première adresse IP
                ip_addresses = x_forwarded_for
                client_ip = ip_addresses[0].strip()
            else:
            # La valeur de X-Forwarded-For est absente, utiliser l'adresse IP directe du client
                client_ip = req.remote_addr

            # Ajouter l'adresse IP du client à la table correspondante de la base de données
            data_add_srv = Serveurs(private_ip=client_ip, name=data['name'], version_sw=data['version_sw'])
            session.add(data_add_srv)
            session.commit()

            resp.status = falcon.HTTP_200
            resp.body = 'Data successfully received and saved.'
            
        except SQLAlchemyError as e:
            # En cas d'erreur SQLAlchemy, effectuer un rollback de la session
            session.rollback()

            resp.status = falcon.HTTP_500
            resp.body = f'Error occurred while saving data: {str(e)}'
        except Exception as e:
            # En cas d'erreur non SQLAlchemy, renvoyer une erreur 500 Internal Server Error
            resp.status = falcon.HTTP_500
            resp.body = f'Error occurred: {str(e)}'

# Ajout des routes à l'application Falcon en associant les classes de ressources aux tables de base de données correspondantes
app.add_route('/srv', APIServeurs(srv))
app.add_route('/', APICPL(cpl))
