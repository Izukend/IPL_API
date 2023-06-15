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
        # Vérification du token d'authentification
        token = req.get_header('Authorization')
        if token and token == f'Bearer {TOKEN}':
            req.context['user'] = {'username': 'izukend'}  # Utilisateur authentifié
        else:
            raise falcon.HTTPUnauthorized('Authentication required', 'Token authentication failed')

# Création de l'application Falcon avec le middleware d'authentification
app = application = falcon.App(middleware=[TokenAuthMiddleware()])

# Configuration de la connexion à la base de données
engine = create_engine("mysql+mysqlconnector://root:password@mysql/falcon_bdd")
metadata = MetaData(bind=engine)
Session = sessionmaker(bind=engine)
session = Session()

# Création des tables de la base de données si elles n'existent pas
Base.metadata.create_all(engine)

# Ajout des routes pour les ressources API
app.add_route('/servers', Servers_data(srv))
app.add_route('/regions', Regions_data(regions))
app.add_route('/cpl', Cpl_data(cpl))
