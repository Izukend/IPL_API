import falcon
import json
from sqlalchemy.exc import SQLAlchemyError
from ipl_api.models import Servers
from datetime import datetime

srv = Servers.__table__

#Transforme le DateTime en string pour pouvoir l'afficher avec la méthode GET
class DateTime:
    @staticmethod
    def json_serial(obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        raise TypeError("Type not serializable")

class Servers_data:

    def __init__(self, table):
        self.post_data = []
        self.table = table

    def on_post(self, req, resp):
        from ipl_api.app import session
        try:
            # Récupérer les données JSON de la requête
            data = json.loads(req.stream.read())
            # Récupérer la valeur de l'en-tête X-Forwarded-For
            x_forwarded_for = req.access_route
            for x_forwarded_for in x_forwarded_for:
                if x_forwarded_for != '127.0.0.1' and x_forwarded_for != '::1':
                    client_ip = x_forwarded_for
                    break
                else:
                    client_ip = req.remote_addr
            
            # Ajouter l'adresse IP du client à la table correspondante de la base de données
            data_add_srv = Servers(private_ip=client_ip, name=data['name'], version_sw=data['version_sw'])
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
        resp.body = json.dumps(rows, default=DateTime.json_serial)
        resp.status = falcon.HTTP_200
