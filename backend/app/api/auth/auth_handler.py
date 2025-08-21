import time
from typing import Dict

import jwt
from decouple import config

from ..models.models_response import UserResponse

JWT_SECRET = config('JWT_SECRET')
JWT_ALGORITHM = config('JWT_ALGORITHM')

def token_response(token: str):
    return {
        "acces_token": token
    }
    
def sign_jwt(user: UserResponse) -> Dict[str,str]:
    minuto = 60
    hora = minuto * 60
    dia = hora * 24
    
    payload = {
        "user_id": user.id,
        "user_name": user.nome,
        "user_email": user.email,
        "user_cargo": user.cargo,
        "user_telefone": user.telefone,
        "user_empresa_nome": user.empresa_nome,
        "expires": time.time() + 3 * dia
    }
    token = jwt.encode(payload,JWT_SECRET,algorithm=JWT_ALGORITHM)
    
    return token_response(token)

def decode_jwt(token: str) -> dict:
    try:
        decoded_token = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return decoded_token if decoded_token["expires"] >= time.time() else None
    except:
        return {}