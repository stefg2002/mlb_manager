import httpx

from fastapi import APIRouter, Request, status, HTTPException

from google_auth import oauth

router = APIRouter()

@router.get("/login", include_in_schema=False)
async def google_login(request: Request):
    redirect_uri = request.url_for('auth_callback')
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/auth", include_in_schema=False)
async def auth_callback(request: Request):
    token = await oauth.google.authorize_access_token(request)
    user = token['userinfo']
    request.session["user"] = {"id": user['sub'], "email": user['email']}
    return user

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def revoke(token: str, request: Request):
    request.session.clear()
    # async with httpx.AsyncClient() as client:
    #     response=await client.post(
    #         f"https://oauth2.googleapis.com/revoke?token={token}"
    #     )
    # if response.status_code != 200:
    #     raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to revoke token")
    