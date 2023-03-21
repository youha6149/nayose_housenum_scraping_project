import os
import shutil

from fastapi import Depends, FastAPI, File, Request, UploadFile
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


@app.post("/test_file_action")
def test_file_action(
    db: Session = Depends(get_nayose_db), file: UploadFile = File(...)
):
    name = f"test_{file.filename}"
    contents = file.file
    upload_filepath = os.path.join(f"{os.getcwd()}/src/csv/", name)
    with open(upload_filepath, "wb+") as upload_dir:
        shutil.copyfileobj(contents, upload_dir)
    return {"filename": name}


@app.post("/execute_scraping")
def execute_scraping(
    db: Session = Depends(get_nayose_db), file: UploadFile = File(...)
):
    # 1. rawファイルの取得
    name = f"test_{file.filename}"
    contents = file.file
    upload_filepath = os.path.join(f"{os.getcwd()}/src/csv/", name)
    with open(upload_filepath, "wb+") as upload_dir:
        shutil.copyfileobj(contents, upload_dir)

    # 2. ファイルをdbに変換する
    # TODO:アップロードされたファイルのパスを_init_dataに渡す方式に変える
    Nayose._init_data()

    housenum0_record = db.query(Nayose).filter_by(housenum=0).all()


# 各スクレイピングクラスのrunにrecordを渡して実行
# データを加工する -> dev_run_processで作業


@app.get("/read_housenum0")
def test_read_nayose_db(db: Session = Depends(get_nayose_db)):
    housenum0_record = db.query(Nayose).filter_by(housenum=0).all()
    print(len(housenum0_record))
    return housenum0_record


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
