from fastapi import APIRouter

from app.api.v1 import admin, auth, contracts, parse, reports, reviews, system, users

api_router = APIRouter()
api_router.include_router(system.router, prefix="/system", tags=["system"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(contracts.router, prefix="/contracts", tags=["contracts"])
api_router.include_router(parse.router, prefix="/contracts", tags=["parse"])
api_router.include_router(reviews.router, tags=["reviews"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
