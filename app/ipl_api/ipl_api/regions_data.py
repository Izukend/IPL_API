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
        # Retrieve the authenticated user from the request context
        user = req.context['user']
        resp.body = f'Authenticated user: {user["username"]}'
        resp.status = falcon.HTTP_200
        try:
            # Retrieve JSON data from the request
            data = json.loads(req.stream.read())
            data_add = Regions(name=data['name'])

            # Add the data to the SQLAlchemy session and save it to the database
            session.add(data_add)
            session.commit()

            resp.status = falcon.HTTP_200
            resp.body = 'Data successfully received and saved.'

        except SQLAlchemyError as e:
            # In case of a SQLAlchemy error, perform a session rollback
            session.rollback()

            resp.status = falcon.HTTP_500
            resp.body = f'Error occurred while saving data: {str(e)}'
        except Exception as e:
            # In case of a non-SQLAlchemy error, return a 500 Internal Server Error
            resp.status = falcon.HTTP_500
            resp.body = f'Error occurred: {str(e)}'

    def on_get(self, req, resp):
        from ipl_api.app import session
        # Retrieve the authenticated user from the request context
        user = req.context['user']
        resp.body = f'Authenticated user: {user["username"]}'
        resp.status = falcon.HTTP_200

        # Execute a SQLAlchemy query to retrieve data from the corresponding table
        query = self.table.select()
        result = session.execute(query)

        # Convert the result rows into a list of dictionaries
        rows = [dict(row) for row in result]

        # Return the data as JSON in the response body
        resp.body = json.dumps(rows)
        resp.status = falcon.HTTP_200
