import streamlit as st
import cv2
import numpy as np
from PIL import Image
import io
import os


def trim_white_space(image):
    """画像の下部の白い余白をトリミングする (右端の列を基準に判定)"""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape
    right_col = gray[:, w - 1]  # 画像の右端の列

    # 右端のピクセルを下から上にスキャンし、明るさの変化が大きい箇所を探す
    for y in range(h - 1, 0, -1):
        if abs(int(right_col[y]) - int(right_col[y - 1])) > 5:  # 明るさの変化を検出
            crop_y = y
            break

    return image[:crop_y, :]


def get_font(font_size):
    """フォントを取得し、存在しない場合はデフォルトフォントにフォールバック"""
    possible_paths = [
        "/System/Library/Fonts/Supplemental/Times New Roman.ttf",  # macOS
        "/usr/share/fonts/truetype/msttcorefonts/times.ttf",  # Linux (MS Core Fonts)
        "/usr/share/fonts/truetype/msttcorefonts/timesnewroman.ttf",  # Linux (別のパス)
        "/usr/share/fonts/truetype/msttcorefonts/Times_New_Roman.ttf",  # さらに別の可能性
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",  # 代替フォント
    ]
    for path in possible_paths:
        if os.path.exists(path):
            return ImageFont.truetype(path, font_size)
    return ImageFont.load_default()


def add_scale_bar(image, magnification):
    """指定された倍率に応じたスケールバーを追加"""
    scale_settings = {"1k": (0.19, "30 μm"), "7k": (0.22, "5 μm"), "10k": (0.19, "3 μm")}

    if magnification not in scale_settings:
        return image

    scale_ratio, scale_text = scale_settings[magnification]

    image = trim_white_space(image)
    h, w, _ = image.shape
    result = image.copy()
    scale_bar_length = int(w * scale_ratio)  # 倍率に応じたスケールバーの長さ
    x_start = int(w * 0.75)  # スケールバーを少し左に移動
    y_start = int(h * 0.92)  # スケールバーの位置を少し上に調整

    # スケールバーを太くする
    cv2.line(result, (x_start, y_start), (x_start + scale_bar_length, y_start), (255, 255, 255), 10)

    # 文字を中央揃えし、スケールバーとの距離を縮める
    font_size = int(w * 0.05)  # フォントサイズを大きくする
    text_x = x_start + (scale_bar_length // 2)  # スケールバーの中央に配置
    text_y = y_start - int(font_size * 1.2)  # スケールバーのすぐ上に配置（距離を縮める）

    # μ (マイクロ) を正しく表示するために PIL を使用
    pil_image = Image.fromarray(cv2.cvtColor(result, cv2.COLOR_BGR2RGB))
    from PIL import ImageDraw, ImageFont

    font = get_font(font_size)
    draw = ImageDraw.Draw(pil_image)
    text_width, text_height = draw.textbbox((0, 0), scale_text, font=font)[2:]
    draw.text((text_x - text_width // 2, text_y), scale_text, font=font, fill=(255, 255, 255))

    return cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)


st.title("自動スケールバー追加アプリ")
st.markdown("**本アプリは日立ハイテクの走査電子顕微鏡(Miniscope TM3030Plus)のSEM画像に対応**")

st.markdown("Created by [Takuo Tachibana](https://takuonon.com/)")

uploaded_file = st.file_uploader("画像をアップロードしてください", type=["jpg", "png", "jpeg"])

magnification = st.selectbox("SEMの倍率を選択", ["1k", "7k", "10k"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    image = np.array(image)

    file_name = os.path.splitext(uploaded_file.name)[0] + "_edited.png"

    if st.button("スケールバーを追加"):
        result_image = add_scale_bar(image, magnification)
        st.image(result_image, caption="スケールバー付き画像", use_container_width=True)

        # 画像のダウンロードボタンを追加
        is_success, buffer = cv2.imencode(".png", result_image)
        if is_success:
            st.download_button(label="画像をダウンロード", data=buffer.tobytes(), file_name=file_name, mime="image/png")
