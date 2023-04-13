from passlib.context import CryptContext

PASSWORD_CONTEXT = CryptContext(schemes = ["bcrypt"])