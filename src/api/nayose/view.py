import glob
import io
import os
import pdb
import traceback
import zipfile

from fastapi import APIRouter, Depends, File, Response, UploadFile
from sqlalchemy.orm import Session

from api.nayose.use_case import NayoseScraperProcess
from model.setting import get_nayose_db

router = APIRouter()


@router.get("/read_output_data")
def read_output_data():
    """スクレイピングによって作成されたCSVデータをZipに圧縮して出力する"""
    try:
        output_dir_path = f"{os.getcwd()}/src/output"
        if not os.path.exists(output_dir_path):
            return {"message": "not exists output data"}

        output_files_path = f"{output_dir_path}/*.csv"

        csv_file_pathes = [path for path in glob.glob(output_files_path)]
        csv_file_pathes.sort(reverse=True)

        # TOP5以外を削除
        if len(csv_file_pathes) > 5:
            for path in reversed(csv_file_pathes):
                os.remove(path)
                if len(os.listdir(output_dir_path)) <= 5:
                    csv_file_pathes = [path for path in glob.glob(output_files_path)]
                    csv_file_pathes.sort(reverse=True)
                    break

        zip_data = io.BytesIO()
        with zipfile.ZipFile(zip_data, "w") as zf:
            for csv_file_path in csv_file_pathes:
                file_name = csv_file_path.split("/")[-1]
                zf.write(csv_file_path, arcname=file_name)

        response = Response(content=zip_data.getvalue(), media_type="application/zip")
        response.headers["Content-Disposition"] = 'attachment; filename="csv_files.zip"'

        return response

    except Exception as e:
        return {"message": traceback.format_exc()}


@router.post("/execute_scraping")
def execute_scraping(
    file_name: str,
    db: Session = Depends(get_nayose_db),
    file: UploadFile = File(...),
):
    try:
        with NayoseScraperProcess(file, file_name) as nayose_process:
            merge_dfs_list = nayose_process.run_scraper(db)
            normalized_merge_df = nayose_process.normalize_output_data(merge_dfs_list)
            normalize_merge_csv_name = nayose_process.create_csv(normalized_merge_df)
            return {"message": "実行完了", "file_name": normalize_merge_csv_name}

    except Exception as e:
        return {"message": "error occured", "traceback": traceback.format_exc()}
