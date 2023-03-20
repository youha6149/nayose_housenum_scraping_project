from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from model.nayose import Nayose
from model.setting import get_nayose_db

app = FastAPI()
origins = ["http://localhost:3000", "http://127.0.0.1:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def index():
    return {"Hello": "World"}


@app.get("")
def test_read_nayose_db(db: Session = Depends(get_nayose_db)):
    housenum0_record = db.query(Nayose).filter_by(housenum=0).all()
    return housenum0_record


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
