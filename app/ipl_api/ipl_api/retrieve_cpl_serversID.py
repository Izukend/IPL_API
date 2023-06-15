import falcon
import json
from sqlalchemy.exc import SQLAlchemyError
from ipl_api.models import Cpl

cpl = Cpl.__table__

class Servers_request_all_for_id:
    def __init__(self, table):
        self.post_data = []
        self.table = table
        
    def on_get(self, req, resp):
        from ipl_api.app import session

        try:
            query = session.query(Cpl).all()

            cpl_data = [{'id_servers': cpl.id_servers, 'uid': cpl.uid, 'name': cpl.name} for cpl in query]

            resp.body = json.dumps(cpl_data)
            resp.status = falcon.HTTP_200

        except SQLAlchemyError as e:
            resp.status = falcon.HTTP_500
            resp.body = f'Une erreur s\'est produite lors de la récupération des données : {str(e)}'
        except Exception as e:
            resp.status = falcon.HTTP_500
            resp.body = f'Une erreur s\'est produite : {str(e)}'
