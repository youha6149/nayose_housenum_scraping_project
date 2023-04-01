import glob
import io
import os
import shutil
import traceback

import pandas as pd
from fastapi import APIRouter, Depends, File, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from model.nayose import Nayose
from model.setting import get_nayose_db
from process.common.utils import Util

router = APIRouter()

# memo:src/main.pyのコード量が多くなって来たため一旦移動。適切なテスト処理として定義が出来次第、再度移動予定
@router.post("/test_streaming_response")
def test_streaming_response(file: UploadFile = File(...)):
    """受け取ったcsvをそのままcsvとして返す。csvを返すテスト"""
    try:
        name = f"test_{file.filename}"
        contents = file.file
        upload_filepath = os.path.join(f"{os.getcwd()}/src/csv/", name)
        with open(upload_filepath, "wb+") as upload_dir:
            shutil.copyfileobj(contents, upload_dir)

        csv_file = io.StringIO()
        df = pd.read_csv(upload_filepath, encoding="utf-8")

        df.to_csv(csv_file, encoding="utf-8")
        csv_file.seek(0)
        return StreamingResponse(
            iter([csv_file.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=sample.csv"},
        )

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


@router.post("/test_init_db")
def test_init_db(db: Session = Depends(get_nayose_db), file: UploadFile = File(...)):
    """名寄せraw_dataをdbに変換するテスト"""
    try:

        name = f"test_{file.filename}"
        contents = file.file
        upload_filepath = os.path.join(f"{os.getcwd()}/src/csv/", name)
        with open(upload_filepath, "wb+") as upload_dir:
            shutil.copyfileobj(contents, upload_dir)

        return {"file_name": name}

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


@router.post("/test_return_normarize_data")
def test_return_normarize_data():
    utils = Util()
    df = pd.read_csv(f"{os.getcwd()}/src/csv/test_scraping.csv")

    df = df.drop("Unnamed: 0", axis=1)
    df["id"] = [i for i in range(1, len(df) + 1)]

    df = utils.data_shaping(df)

    csv_file = io.StringIO()
    df.to_csv(csv_file, encoding="utf-8")
    csv_file.seek(0)
    return StreamingResponse(
        iter([csv_file.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=sample.csv"},
    )


@router.get("/read_housenum0")
def test_read_nayose_db(db: Session = Depends(get_nayose_db)):
    nayose = Nayose()
    housenum0_record = nayose.read_nayose_data(db)
    print(len(housenum0_record))
    return housenum0_record
