import os
import glob
from pathlib import Path
from pdf2image import convert_from_path
from PIL import Image
import pyocr

# 定数定義
POPPLER_DIR = "poppler/Library/bin"
PDF_DIR = "pdf"
IMAGES_DIR = "images"
TXT_DIR = "txt"

# PDF を PNG 画像に変換
def pdf_to_image():
    pdfs_path = get_pdfs_path(PDF_DIR)
    for pdf_path in pdfs_path:
        print('変換中ファイル：' + os.path.basename(pdf_path))
        pdf_image = pdf_to_imageobject(pdf_path, POPPLER_DIR)
        output_dir = os.path.join(IMAGES_DIR, os.path.splitext(os.path.basename(pdf_path))[0])
        pillowimage_to_imagefile(pdf_image, output_dir)

# PDF ファイルのパスを一括取得
def get_pdfs_path(input_dir):
    pdf_path = os.path.join(Path(__file__).parent, input_dir)
    pdfs_path = glob.glob(os.path.join(pdf_path, '*.pdf'))
    return pdfs_path

# Image ファイルのパスを一括取得(imageフォルダのpngに到達する最下層まで取得)
def get_images_path(input_dir):
    image_path = os.path.join(Path(__file__).parent, input_dir)
    list = [image_path, "**", "*.png"]
    images_path = glob.glob(os.path.join(*list), recursive=True)
    return images_path

# txt ファイル名の作成
def make_txt_file_root(input_file_name, root_dir):
    list = [root_dir, input_file_name + ".txt"]
    txt_file_path = os.path.join(*list)
    return txt_file_path

# PDF を Pillow Image オブジェクトに変換
def pdf_to_imageobject(pdf_path, poppler_dir, dpi = 300):
    poppler_path = os.path.join(Path(__file__).parent, poppler_dir)
    images = convert_from_path(pdf_path=pdf_path, poppler_path=poppler_path, dpi=dpi)
    return images

# Pillow Image オブジェクトを画像ファイルに変換し保存
def pillowimage_to_imagefile(images, output_dir):
    image_dir = os.path.join(Path(__file__).parent, output_dir)
    os.makedirs(image_dir, exist_ok=True)
    for i, image in enumerate(images):
        image_name = str(i + 1) + ".png"
        image_path = os.path.join(image_dir, image_name)
        image.save(image_path, "PNG")

def ocr():
    # -----tesseractとpyocrの準備-----
    # pyocrが使えることを確認する
    tools = pyocr.get_available_tools()
    # tesseractのみダウンロードしたため0番目を指定
    tool = tools[0]

    images_path = get_images_path(IMAGES_DIR)

    # -----image変換からocr処理-----
    for image_path in images_path:
        print('OCR変換中：' + image_path)
        img = Image.open(image_path)
        txt = tool.image_to_string(
            img,
            lang='jpn+eng',
            builder=pyocr.builders.TextBuilder(tesseract_layout=6)
        )
        
        # imageファイルパスからtxtファイルパスを生成する
        dirname_for_image = os.path.dirname(image_path)
        dirname_for_txt = dirname_for_image.replace(IMAGES_DIR, TXT_DIR)
        os.makedirs(dirname_for_txt, exist_ok=True)

        txt_file_name = os.path.splitext(os.path.basename(image_path))[0]
        txt_file_path= make_txt_file_root(txt_file_name, dirname_for_txt)

        # 実行結果をテキストファイルに書き込む
        with open(txt_file_path, "w", encoding='UTF-8') as o:
            print(txt, file=o)

if __name__ == "__main__":
    pdf_to_image()
    ocr()