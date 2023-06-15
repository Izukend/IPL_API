import falcon
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from ipl_api.servers_data import Servers_data, srv
from ipl_api.cpl_data import Cpl_data, cpl
from ipl_api.regions_data import Regions_data, regions
from ipl_api.models import Base
# Définition du token d'authentification
TOKEN = 'githubtoken'

class TokenAuthMiddleware:
    def process_request(self, req, resp):

        token = req.get_header('Authorization')
        if token and token == f'Bearer {TOKEN}':
            req.context['user'] = {'username': 'izukend'}
        else:
            raise falcon.HTTPUnauthorized('Authentication required', 'Token authentication failed')


app = application = falcon.App(middleware=[TokenAuthMiddleware()])

engine = create_engine("mysql+mysqlconnector://root:password@mysql/falcon_bdd")
metadata = MetaData(bind=engine)
Session = sessionmaker(bind=engine)
session = Session()
Base.metadata.create_all(engine)

app.add_route('/servers', Servers_data(srv))
app.add_route('/regions', Regions_data(regions))
app.add_route('/cpl', Cpl_data(cpl))
