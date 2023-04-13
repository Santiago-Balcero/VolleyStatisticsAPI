from pydantic import BaseModel

class AuthResponse(BaseModel):
	accessToken: str
	refreshToken: str
	token_type: str = "bearer"
 
class RefreshToken(BaseModel):
    refreshToken: str