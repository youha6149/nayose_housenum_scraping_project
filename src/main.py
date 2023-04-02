from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.nayose.view import router as nayose_router
from api.test.api_test import router as tests_router

app = FastAPI()
origins = ["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:8501/"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(nayose_router)
app.include_router(tests_router)


@app.get("/")
def index():
    return {"Hello": "World"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
