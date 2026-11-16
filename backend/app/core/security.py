import os
import secrets
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials

basic = HTTPBasic()

def require_admin(credentials: HTTPBasicCredentials = Depends(basic)):
    valid_user = secrets.compare_digest(credentials.username.encode(), b"admin")
    valid_password = secrets.compare_digest(credentials.password.encode(), os.environ["ADMIN_PASSWORD"].encode())
    if not (valid_user and valid_password):
        raise HTTPException(401, "Требуется вход администратора", headers={"WWW-Authenticate": "Basic"})
