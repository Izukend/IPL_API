import falcon
import json
import pytz
from sqlalchemy.exc import SQLAlchemyError
from ipl_api.models import Servers
from datetime import datetime

srv = Servers.__table__
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
            data = json.loads(req.stream.read())
            x_forwarded_for = req.access_route
            for x_forwarded_for in x_forwarded_for:
                if x_forwarded_for != '127.0.0.1' and x_forwarded_for != '::1':
                    client_ip = x_forwarded_for
                    break
                else:
                    client_ip = req.remote_addr

            paris = pytz.timezone('Europe/Paris')
            heure_actuelle = datetime.now(tz=paris)
            last_seen_fuseau= heure_actuelle.strftime('%Y-%m-%d %H:%M:%S')

            data_add_srv = Servers(private_ip=client_ip, name=data['name'], version_sw=data['version_sw'], last_seen=last_seen_fuseau)
            session.add(data_add_srv)
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
        from ipl_api.app import session
        user = req.context['user']
        resp.body = f'Authenticated user: {user["username"]}'
        resp.status = falcon.HTTP_200

        query = self.table.select()
        result = session.execute(query)

        rows = [dict(row) for row in result]

        resp.body = json.dumps(rows, default=DateTime.json_serial)
        resp.status = falcon.HTTP_200
