import falcon
import json
from sqlalchemy.exc import SQLAlchemyError
from ipl_api.models import Regions

regions = Regions.__table__

class Regions_data:
    def __init__(self, table):
        self.post_data = []
        self.table = table

    def on_post(self, req, resp):
        from ipl_api.app import session
        # Récupérer l'utilisateur authentifié à partir du contexte de la requête
        user = req.context['user']
        resp.body = f'Authenticated user: {user["username"]}'
        resp.status = falcon.HTTP_200
        try:
            # Récupérer les données JSON de la requête
            data = json.loads(req.stream.read())
            data_add = Regions(name=data['name'])

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
        from ipl_api.app import session
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
