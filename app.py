import streamlit as st
import cv2
import numpy as np
import pytesseract
from PIL import Image

def extract_scale_text(image):
    """OCRを使って画像右下のスケール値を抽出する"""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape
    roi = gray[int(h * 0.9):, int(w * 0.7):]  # 右下部分をトリミング
    text = pytesseract.image_to_string(roi, config='--psm 6')
    return text.strip()

def find_scale_bar(image):
    """画像内の黒いスケールバーを検出する"""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 100, 200)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    max_contour = max(contours, key=cv2.contourArea)  # 最大の輪郭を取得
    x, y, w, h = cv2.boundingRect(max_contour)
    return x, y, w, h

def add_scale_bar(image, scale_length, scale_text):
    """新しいスケールバーを画像の右下に追加"""
    h, w, _ = image.shape
    result = image.copy()
    scale_bar_length = int(w * 0.1)  # 画像の10%の長さ
    x_start = int(w * 0.85)
    y_start = int(h * 0.95)
    cv2.line(result, (x_start, y_start), (x_start + scale_bar_length, y_start), (255, 255, 255), 3)
    cv2.putText(result, scale_text, (x_start, y_start - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    return result

st.title("自動スケールバー追加アプリ")

uploaded_file = st.file_uploader("画像をアップロードしてください", type=["jpg", "png", "jpeg"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    image = np.array(image)
    
    scale_text = extract_scale_text(image)
    detected_scale = "100 µm" if not scale_text else scale_text  # デフォルト値を設定
    
    user_scale = st.text_input("スケールバーのラベル (例: 100 nm, 10 µm)", value=detected_scale)
    
    if st.button("スケールバーを追加"):
        x, y, w, h = find_scale_bar(image)
        result_image = add_scale_bar(image, w // 3, user_scale)
        st.image(result_image, caption="スケールバー付き画像", use_column_width=True)