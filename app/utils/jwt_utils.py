import datetime

import jwt

from config import Config


def generate_jwt():
    expiration_time = datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(seconds=Config.EXPIRATION_JWT)
    token = jwt.encode(
        {
            "role": 'ADMIN',
            "exp": expiration_time
        }, 
        Config.SECRET_KEY
    )

    return token
