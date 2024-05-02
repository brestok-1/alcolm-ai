from fastapi.templating import Jinja2Templates
from fastapi.requests import Request

from project.bot import bot_router

template = Jinja2Templates(directory='project/bot/templates')


@bot_router.get('/', name='main')
async def main(request: Request):
    return template.TemplateResponse("home.html", {'request': request})
