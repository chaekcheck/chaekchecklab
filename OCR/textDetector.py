import easyocr

from PIL import Image, ImageOps
import numpy as np
 
from collections import deque

def change_to_black_text(text_box):
    # 흑백 이미지로 전환
    text_box = text_box.convert("L")

    np_img = np.array(text_box)
    np_img_1d = np_img.flatten()

    histogram = np.bincount(np_img_1d, minlength=256)  # 0~255의 값에 대한 빈도 계산
    # $$$ threshold 수정하기
    threshold = np_img.size/256

    filtered_arr = np.where(histogram < threshold, 0, histogram)
    filter_img = np_img_1d[filtered_arr[np_img_1d] > 0]

    # 이미지 밝기 값들의 평균과 표준편차 계산
    mean_brightness = np.mean(filter_img)
    std_brightness = np.std(filter_img)

    # 표준정규화 (Z-score normalization)
    normalized_img = (filter_img - mean_brightness) / std_brightness

    normalized_mean = 255 * (np.mean(normalized_img) - normalized_img.min()) / (normalized_img.max() - normalized_img.min())

    # 이진화
    # v = 72*(normalized_img.max() - normalized_img.min())/255 + normalized_img.min()
    # th = v * std_brightness + mean_brightness
    # binary_img = text_box.point(lambda x: 0 if x < th else 255, '1')

    if normalized_mean < 127:
        text_box = ImageOps.invert(text_box)

    # 정규화된 결과를 다시 이미지로 변환 (시각화를 위해 값 조정)
    # normalized_img_scaled = 255 * (normalized_img - normalized_img.min()) / (normalized_img.max() - normalized_img.min())
    # normalized_img_scaled = normalized_img_scaled.astype(np.uint8)
    # if np.mean(normalized_img_scaled) < 127:
    #     text_box = ImageOps.invert(text_box)

    return text_box

class TextDetector:
    def __init__(self) -> None:
        self.reader = easyocr.Reader(['ko','en'])

    def crop(self, object_image: Image.Image):
        img_arr = np.array(object_image)

        text_box_list = []
        prob_list = []

        result_td = self.reader.readtext(img_arr)
        for i, (bbox, text, prob) in enumerate(result_td):
            # print(bbox)

            # 좌상단과 우하단 좌표를 사용해 자를 수 있음
            x_min = int(min(bbox[0][0], bbox[1][0], bbox[2][0], bbox[3][0]))
            y_min = int(min(bbox[0][1], bbox[1][1], bbox[2][1], bbox[3][1]))
            x_max = int(max(bbox[0][0], bbox[1][0], bbox[2][0], bbox[3][0]))
            y_max = int(max(bbox[0][1], bbox[1][1], bbox[2][1], bbox[3][1]))

            # 이미지 자르기 (좌표는 (left, upper, right, lower))
            text_box = object_image.crop((x_min, y_min, x_max, y_max))
            text_box_list.append(text_box)
            prob_list.append(prob)
        return text_box_list, prob_list

    def filtering_title_box(self, text_box_list, prob_list):
        if not text_box_list:
            return [], [], [], []

        size_list = [sorted(b.size) for b in text_box_list]

        max_char_size = max(next(zip(*size_list)))
        char_size_range = [max_char_size*0.8, max_char_size*1.2]

        title_boxes = []
        title_probs = []
        etc_boxes = []
        etc_probs = []

        for tb, prob in zip(text_box_list, prob_list):
            if char_size_range[0] <= min(tb.size) <= char_size_range[1]:
                title_boxes.append(change_to_black_text(tb))
                title_probs.append(prob)
            else:
                etc_boxes.append(change_to_black_text(tb))
                etc_probs.append(prob)
        return title_boxes, title_probs, etc_boxes, etc_probs

    def crop_all(self, object_image: Image.Image):
        text_box_list, prob_list = self.crop(object_image)
        rt_text_box_list, rt_prob_list = self.crop(object_image.rotate(90, expand=True))

        tb_list = self.filtering_title_box(text_box_list, prob_list)
        rt_tb_list = self.filtering_title_box(rt_text_box_list, rt_prob_list)

        return tb_list, rt_tb_list
    
    def get_title_boxes(self, object_image: Image.Image):
        # object_image = Image.open(object_image_path)
        text_box_list = self.crop_all(object_image)
        # rt_text_box_list, rt_prob_list = self.crop_all(object_image.rotate(90, expand=True))
        title_boxes, etc_boxes = self.filtering_title_box(text_box_list)

        return title_boxes, etc_boxes

# x1, x2, x3, x4 = bbox
# w = x2[0] - x1[0]
# h = x3[1] - x2[1]
# print(f"글자 수: {math.ceil(long/short)}")