from fastapi import APIRouter

router = APIRouter(tags=["registration"])

@router.post("/register")
async def register_user_simple():
    return {"message": "Registration endpoint working!", "status": "success"}

@router.get("/register/health")
async def registration_health():
    return {"service": "registration", "status": "healthy"}
