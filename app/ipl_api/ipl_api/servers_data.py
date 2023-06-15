import falcon
import json
from sqlalchemy.exc import SQLAlchemyError
from ipl_api.models import Servers

srv = Servers.__table__

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
            """
            if x_forwarded_for:
                ip_addresses = x_forwarded_for
                client_ip = ip_addresses[0]
            else:
                client_ip = req.remote_addr
"""
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
