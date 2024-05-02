from fastapi import APIRouter

bot_router = APIRouter(
    prefix=''
)

from project.bot import views
