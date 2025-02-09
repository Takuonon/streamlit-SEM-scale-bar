import os
import streamlit as st


def list_fonts():
    font_dirs = [
        "/usr/share/fonts",
        "/usr/share/fonts/truetype",
        "/usr/share/fonts/truetype/dejavu",
        "/usr/share/fonts/truetype/msttcorefonts",
        "/usr/share/fonts/truetype/liberation",
    ]

    font_files = []
    for font_dir in font_dirs:
        if os.path.exists(font_dir):
            font_files.extend([os.path.join(font_dir, f) for f in os.listdir(font_dir)])

    return font_files


st.title("フォントディレクトリの内容")

if st.button("フォント一覧を取得"):
    fonts = list_fonts()
    st.text_area("フォントファイル一覧", "\n".join(fonts), height=300)
