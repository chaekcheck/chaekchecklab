import streamlit as st
import pandas as pd
from datetime import datetime
import os
from PIL import Image

# st.header('ChaeckCheck 책쳌')

# if st.button('책장 사진 업로드 하기'):
#     st.write('내 책장 분석중..')
# else:
#     st.write('Goodbye')

# 파일 업로드 함수
def save_uploaded_file(directory, file):
    if not os.path.exists(directory):  # 해당 이름의 폴더가 존재하는지 여부 확인
        os.makedirs(directory)  # 폴더가 없다면 폴더를 생성한다.

    with open(os.path.join(directory, file.name), 'wb') as f:  # 해당 경로의 폴더에서 파일의 이름으로 생성
        f.write(file.getbuffer())  # 해당 내용은 Buffer로 작성
        # 기본적으로 이미지는 buffer로 저장되고 출력할때도 buffer로 출력
        
    return st.success('파일 업로드 성공')

# Streamlit 앱
st.title('ChaechCheck 책쳌')

st.subheader('내 책장 사진')
image_file = st.file_uploader("이미지를 업로드 하세요.", type=['png', 'jpg', 'jpeg'])

if image_file is not None:
    current_time = datetime.now()
    filename = current_time.isoformat().replace(":", "_") + os.path.splitext(image_file.name)[-1]  # 확장자 유지
    image_file.name = filename
    save_uploaded_file('uploads', image_file)

    img = Image.open(image_file)
	# 경로에 있는 이미지 파일을 통해 변수 저장
    st.image(img)
	# 이미지를 보여준다

