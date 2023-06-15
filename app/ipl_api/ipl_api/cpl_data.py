import falcon
import json
from sqlalchemy.exc import SQLAlchemyError
from ipl_api.models import Cpl

cpl = Cpl.__table__

class Cpl_data:
    def __init__(self, table):
        self.post_data = []
        self.table = table

    def on_post(self, req, resp):
        from ipl_api.app import session
        user = req.context['user']
        resp.body = f'Authenticated user: {user["username"]}'
        resp.status = falcon.HTTP_200
        try:
            data = json.loads(req.stream.read())
            data_add = Cpl(id=data['id'], uid=data['uid'], name=data['name'])

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
        from ipl_api.app import session

        user = req.context['user']
        resp.body = f'Authenticated user: {user["username"]}'
        resp.status = falcon.HTTP_200

        query = self.table.select()
        result = session.execute(query)

        rows = [dict(row) for row in result]

        resp.body = json.dumps(rows)
        resp.status = falcon.HTTP_200
