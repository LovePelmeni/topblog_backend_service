import easyocr
from PIL import Image

import re
import os
import cv2

import matplotlib.pyplot as plt
import matplotlib.patches as patches

from pathlib import Path
import math
import typing

class TextDetectionModel(object):
    def __init__(self):
        self.reader = easyocr.Reader(['ru', 'en'])

    def process_image(self, path, type_of_social: typing.Literal['zn', 'yt', 'tg', 'vk'], show=False):
        path_tmp = self.upscale_photo(path, 'tmp')
        result_of_process = self.reader.readtext(path, paragraph=False)

        if len(result_of_process) == 0:
            ValueError("Не удалось распознать текст")
            return None
        data = self.transform_data(result_of_process)

        result = self.filters(data, type_of_social)
        if show:
            self.plot(path, result_of_process)
        return result

    def find_closest_number(self, text_key, dict_of_bboxes, type_of_social="None"):
        closest_row = None
        closest_distance = float('inf')

        for i, row in enumerate(dict_of_bboxes):
            if row != text_key:
                if type_of_social=="zn" and self.is_lower(text_key["coordinates"], row["coordinates"]) and self.get_numbers(row["label"]):
                    distance = self.calculate_distance(text_key["coordinates"], row["coordinates"])

                    if distance < closest_distance:
                        closest_distance = distance
                        closest_row = row

                elif type_of_social=='yt2' and (self.get_numbers(row["label"]) or self.convert_to_number(row["label"])):
                    target_center = (text_key["coordinates"][0][1] + text_key["coordinates"][2][1]) / 2
                    if abs(target_center - ((row["coordinates"][0][1] + row["coordinates"][2][1]) / 2)) < 20:
                        if row["coordinates"][0][0] > text_key["coordinates"][2][0]:
                            distance = self.calculate_distance(text_key["coordinates"], row["coordinates"])
                            if distance < closest_distance:
                                closest_distance = distance
                                closest_row = row

                elif type_of_social=='vk' and (self.get_numbers(row["label"]) or self.convert_short_numbers_with_k(row["label"])):
                    distance = self.calculate_distance(text_key["coordinates"], row["coordinates"])

                    if distance < closest_distance:
                        closest_distance = distance
                        closest_row = row

                elif type_of_social=='tg' and self.is_percent_number(row["label"]):
                    distance = self.calculate_distance(text_key["coordinates"], row["coordinates"])

                    if distance < closest_distance:
                          closest_distance = distance
                          closest_row = row

                elif type_of_social=='yt2' and self.get_numbers(row["label"]):
                    distance = self.calculate_distance(text_key["coordinates"], row["coordinates"])

                    if distance < closest_distance:
                        closest_distance = distance
                        closest_row = row

        if type_of_social=='yt2' and self.convert_to_number(closest_row['label']):
            return self.convert_to_number(closest_row['label'])
        if type_of_social=='vk' and self.convert_short_numbers_with_k(closest_row['label']):
            return self.convert_short_numbers_with_k(closest_row['label'])
        if type_of_social=='tg' and self.is_percent_number(closest_row['label']):
            return self.is_percent_number(closest_row['label'])

        return self.get_numbers(closest_row['label'])

    def plot(self, path, result_of_process):
        img = plt.imread(path)

        fig, ax = plt.subplots(figsize=(10, 10))
        ax.imshow(img)

        for bbox, text, confidence in result_of_process:
            rect = patches.Rectangle(
                (bbox[0][0], bbox[0][1]), bbox[1][0] - bbox[0][0], bbox[3][1] - bbox[0][1],
                linewidth=1, edgecolor='r', facecolor='none'
            )
            ax.add_patch(rect)
            ax.text(
                bbox[0][0], bbox[0][1], f"{text} ({confidence:.2f})",
                fontsize=1, color='r', verticalalignment='bottom',
                bbox=dict(facecolor='white', alpha=0.5, edgecolor='none', boxstyle='round')
            )

        plt.show()

    def filters(self, dict_text_box, type_of_social):
        matching_rows = []
        key_row= None

        key_row_vk_1 = None
        key_row_vk_2 = None
        key_row_vk_3 = None
        key_row_vk_4 = None

        yt_subs, yt_watches = None, None
        # Ищем dzen
        if type_of_social == "zn":
          for item in dict_text_box:
              label = item["label"]
              if label in ["дочитывания и просмотры", "дочитывания"]:
                  key_row = item

          if key_row != None:
              return self.find_closest_number(key_row, dict_text_box, type_of_social)

        elif type_of_social == "yt1":
          # Ищем подписичков в YouTube
          for item in dict_text_box:
              label = item["label"]
              if "подпис" in label and len(re.findall(r'\w+', label)) == 1:
                key_row = item

          if key_row != None:
              return self.find_closest_number(key_row, dict_text_box)

        elif type_of_social == "yt2":
          # Ищем просмотры в YouTube
          for item in dict_text_box:
              label = item["label"]
              if "просмотры" in label and len(re.findall(r'\w+', label)) == 1:
                  key_row = item

          if key_row != None:
              return self.find_closest_number(key_row, dict_text_box, type_of_social)

        elif type_of_social == 'tg':
          for item in dict_text_box:
              label = item["label"]
              if "подписчиков читают" in label:
                  key_row = item

          if key_row != None:
              return self.find_closest_number(key_row, dict_text_box, type_of_social)

          for item in dict_text_box:
              label = item["label"]
              if "vr" in label and len(re.findall(r'\w+', label)) == 1:
                  key_row = item

          if key_row != None:
              return self.find_closest_number(key_row, dict_text_box, type_of_social)

          for item in dict_text_box:
              label = item["label"]
              if "просмотров постов" in label:
                  key_row = item

          if key_row != None:
              return self.find_closest_number(key_row, dict_text_box, type_of_social)

          for item in dict_text_box:
              label = item["label"]
              if "читают" in label:
                  key_row = item

          if key_row != None:
              return self.find_closest_number(key_row, dict_text_box, type_of_social)

        elif type_of_social == "vk":
          # Ищем друзей и подписчиков в VK
          friends_number = 0
          subs_1_number = 0
          subs_2_number = 0
          subs_3_number = 0
          subs_4_number = 0

          for item in dict_text_box:
              label = item["label"]
              if "друзей" in label and len(re.findall(r'\w+', label)) == 1:
                  key_row_vk_1 = item
          if key_row_vk_1 != None:
              if self.get_numbers(key_row_vk_1['label']):
                friends_number = self.get_numbers(key_row_vk_1['label'])
              else:
                friends_number = self.find_closest_number(key_row_vk_1, dict_text_box, type_of_social)

          for item in dict_text_box:
              label = item["label"]
              if "подписчик" in label and len(re.findall(r'\w+', label)) == 1:
                  key_row_vk_2 = item
          if key_row_vk_2 != None:
              if self.get_numbers(key_row_vk_2['label']):
                subs_2_number = self.get_numbers(key_row_vk_2['label'])
              else:
                subs_2_number = self.find_closest_number(key_row_vk_2, dict_text_box, type_of_social)

          for item in dict_text_box:
              label = item["label"]
              if "участника" in label and len(re.findall(r'\w+', label)) == 1:
                  key_row_vk_3 = item
          if key_row_vk_3 != None:
              if self.get_numbers(key_row_vk_3['label']):
                 subs_3_number = self.get_numbers(key_row_vk_3['label'])
              else:
                 subs_3_number = self.find_closest_number(key_row_vk_3, dict_text_box, type_of_social)

          for item in dict_text_box:
              label = item["label"]
              if "друг" in label and len(re.findall(r'\w+', label)) == 1:
                  key_row_vk_4 = item
          if key_row_vk_4 != None:
              if self.get_numbers(key_row_vk_3['label']):
                  subs_4_number = self.get_numbers(key_row_vk_4['label'])
              else:
                  subs_4_number = self.find_closest_number(key_row_vk_4, dict_text_box, type_of_social)

          return sum([friends_number, subs_1_number,
                      subs_2_number, subs_3_number, subs_4_number])
        return None


    @staticmethod
    def convert_to_number(input_str):
        multipliers = {
            'тыс': 1000,
            'млн': 1000000,
            'млрд': 1000000000
        }

        pattern = r'(\d+(\.\d+)?)\s*(\S+)\s*'
        match = re.match(pattern, input_str.replace(',', '.'))

        if match:
            try:
                number = float(match.group(1))
                multiplier = multipliers.get(match.group(3).lower())
                if multiplier is not None:
                    result = int(number * multiplier)
                    return result
            except:
                 return None

        return None


    @staticmethod
    def upscale_photo(input_path, tmp_dir):
        image = cv2.imread(input_path)
        filename = Path(input_path).name

        if not os.path.exists(tmp_dir):
            os.mkdir(tmp_dir)

        new_width = int(image.shape[1] * 3)  # Увеличение ширины в 3 раза
        new_height = int(image.shape[0] * 3)  # Увеличение высоты в 3 раза
        resized_image = cv2.resize(image, (new_width, new_height))
        cv2.imwrite(os.path.join(tmp_dir, filename), resized_image)

        return os.path.join(tmp_dir, filename)

    @staticmethod
    def transform_data(input_data):
        transformed_data = []

        for item in input_data:
            coordinates = item[0]
            label = item[1]
            confidence = item[2]

            transformed_item = {
                "coordinates": coordinates,
                "label": label.lower(),
                "confidence": confidence
            }

            transformed_data.append(transformed_item)

        return transformed_data

    @staticmethod
    def convert_short_numbers_with_k(text):
        if 'k' in text or 'к' in text:
            number_part = text.replace('k', '').replace('к', '')
            try:
                numeric_value = float(number_part) * 1000
                return int(numeric_value)
            except ValueError:
                return None
        else:
            return None

    @staticmethod
    def is_percent_number(string):
        string = string.strip()  # Remove any leading or trailing spaces

        if string.endswith("%"):
            # Remove the percent sign and check if the rest is a valid number
            number_part = string[:-1]
            try:
                return float(number_part)
            except ValueError:
                return False
        else:
            return False

    @staticmethod
    def get_numbers(string):
        # Ищем цифру в строке, при этом если нашлось больше 1 цифры возвращаем False, или если не нашлось
        # Также если есть +, такое число не берем
        numbers = re.findall(r'\d+', string)
        if len(numbers) == 1 and '+' not in string:
            return int(numbers[0])
        else:
            return False

    @staticmethod
    def calculate_distance(coords1, coords2):
        center1 = [(coords1[0][0] + coords1[2][0]) / 2, (coords1[0][1] + coords1[2][1]) / 2]
        center2 = [(coords2[0][0] + coords2[2][0]) / 2, (coords2[0][1] + coords2[2][1]) / 2]

        return math.sqrt((center1[0] - center2[0])**2 + (center1[1] - center2[1])**2)

    @staticmethod
    def is_lower(coords1, coords2):
        center1 = (coords1[0][1] + coords1[2][1]) / 2
        center2 = (coords2[0][1] + coords2[2][1]) / 2

        if center1 < center2:
            return True
        return False