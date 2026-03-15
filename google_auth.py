from authlib.integrations.starlette_client import OAuth
from starlette.config import Config


oauth = OAuth(Config('.google.env'))
oauth.register(
    name='google',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)
