from fastapi import FastAPI

from app.database.init import init_db
from app.routes.authentication import router as auth_router
from app.routes.profile import router as profile_router


app = FastAPI(
    title='LinkRepo - API',
)

app.include_router(auth_router)
app.include_router(profile_router)


if __name__ == '__main__':
    init_db()
