import falcon
import json
from sqlalchemy.exc import SQLAlchemyError
from ipl_api.models import Servers
from datetime import datetime

srv = Servers.__table__

# Convert DateTime to a string to display it using the GET method
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
            # Retrieve JSON data from the request
            data = json.loads(req.stream.read())
            # Retrieve the value of the X-Forwarded-For header
            x_forwarded_for = req.access_route
            for x_forwarded_for in x_forwarded_for:
                if x_forwarded_for != '127.0.0.1' and x_forwarded_for != '::1':
                    client_ip = x_forwarded_for
                    break
                else:
                    client_ip = req.remote_addr
            
            # Add the client's IP address to the corresponding table in the database
            data_add_srv = Servers(private_ip=client_ip, name=data['name'], version_sw=data['version_sw'])
            session.add(data_add_srv)
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

        # Return the data as JSON in the response body, with DateTime converted to a string
        resp.body = json.dumps(rows, default=DateTime.json_serial)
        resp.status = falcon.HTTP_200
