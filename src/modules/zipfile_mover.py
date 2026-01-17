"""
『source_folder』と『destination_folder』を指定すことで
source_folderに入っている全てのzipファイルをdestination_folderに移動するプログラム
"""

import shutil
import glob
import os


def move_zipfiles(source_folder, destination_folder):
    # フォルダ内のファイル名のリスト群を取得
    files_paths = glob.glob(source_folder + "/*.zip")

    # ファイル名のリスト作成
    filename_list = []
    for file_path in files_paths:
        file_name = os.path.basename(file_path)
        filename_list.append(file_name)

    # print(filename_list)

    for file_name in filename_list:
        # ファイルを移動
        shutil.move(source_folder + "/" + file_name, destination_folder + "/" + file_name)
        print(f"{file_name}ファイルを{source_folder}から{destination_folder}に移動しました。")


if __name__ == "__main__":
    # 移動元と移動先のパスを指定
    source_folder = r"C:\Users\SONY\Downloads"
    destination_folder = r"C:\Users\SONY\PycharmProjects\pythonProject\TDnet_XBRL\zip_files"

    # ファイルを移動
    move_zifiles(source_folder, destination_folder)
