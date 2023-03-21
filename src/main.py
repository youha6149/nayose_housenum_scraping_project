import glob
import os
import shutil
import traceback

from fastapi import Depends, FastAPI, File, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from model.nayose import Nayose
from model.setting import get_nayose_db
from process.homemate.run import run as run_homemate
from process.homes.run import run as run_homes
from process.suumo.run import run as run_suumo

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
    try:
        name = f"test_{file.filename}"
        contents = file.file
        upload_filepath = os.path.join(f"{os.getcwd()}/src/csv/", name)
        with open(upload_filepath, "wb+") as upload_dir:
            shutil.copyfileobj(contents, upload_dir)

        Nayose._init_data(upload_filepath)

        return {"filename": name}
    except Exception as e:
        db_dir = f"{os.getcwd()}/src/db/*.db"
        if os.path.exists(db_dir):
            for file_path in glob.glob(db_dir):
                os.remove(file_path)

        csv_dir = f"{os.getcwd()}/src/csv/*.csv"
        if os.path.exists(csv_dir):
            for file_path in glob.glob(csv_dir):
                os.remove(file_path)

        print(traceback.format_exc())
        return e


# TODO:すべてのデータ作業が終わったらdbファイルの削除を行う
@app.post("/execute_scraping")
def execute_scraping(
    db: Session = Depends(get_nayose_db), file: UploadFile = File(...)
):
    try:
        # 1. rawファイルの取得
        name = f"test_{file.filename}"
        contents = file.file
        upload_filepath = os.path.join(f"{os.getcwd()}/src/csv/", name)
        with open(upload_filepath, "wb+") as upload_dir:
            shutil.copyfileobj(contents, upload_dir)

        # 2. ファイルをdbに変換する
        Nayose._init_data(upload_filepath)

        # 3. 各スクレイピング処理の実行
        # TODO:各スクレイピング処理で作成されたデータを共通化する
        # housenum0_record = db.query(Nayose).filter_by(housenum=0).all()
        # run_suumo(housenum0_record)
        # run_homes(housenum0_record)
        # run_homemate(housenum0_record)

    # 4. 使用したdbファイルを削除する
    # エラー時に使用したCSVとdbファイルを削除するようにする
    except Exception as e:
        db_dir = f"{os.getcwd()}/src/db/*.db"
        if os.path.exists(db_dir):
            for file_path in glob.glob(db_dir):
                os.remove(file_path)

        csv_dir = f"{os.getcwd()}/src/csv/*.csv"
        if os.path.exists(csv_dir):
            for file_path in glob.glob(csv_dir):
                os.remove(file_path)

        print(traceback.format_exc())
        return e


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
