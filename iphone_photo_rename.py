import sys, os
import time
from tkinter import messagebox
from tkinter import filedialog
from PIL import Image
from PIL.ExifTags import TAGS

## 변환하고자하는 원본파일의 확장자명을 여기에 사전 기입해야한다. (대소문자 구분한다)
applicable_file_type = ['.JPG', '.PNG', '.HEIC', '.MOV', '.jpg', '.mp4', '.png']

## 이름 변환 실패한 파일 리스트
failed_files = []

class GUI:
    def iphone_photo_folder_path(self):
        str_title = 'Select folder where iphone photo/movie files exist'
        iphone_photo_folder = filedialog.askdirectory(initialdir='C:/', title=str_title)
        if iphone_photo_folder == '':
            messagebox.showwarning('Warning', 'No folder path selected. Please try again')
            sys.exit()
        print('-- Folder path : ', iphone_photo_folder)

        return iphone_photo_folder


def get_image_path(root_dir):
    result_list = []
    for(root, dirs, files) in os.walk(root_dir):
        if len(files) > 0:
            for file_name in files:
                file_path = os.path.join(root, file_name)
                result_list.append(file_path)

    print('-- Total files num :', len(result_list))

    return result_list

## 실제 EXIF "찍은 날짜" 정보를 읽는 함수
def get_photo_taken_date(f):
    try:
        image = Image.open(f)
        exif_data = image._getexif()

        if exif_data:
            for tag_id, value in exif_data.items():
                tag_name = TAGS.get(tag_id, tag_id)
                if tag_name == "DateTimeOriginal":
                    print(f'{f} -> EXIF_Taken_time : {value}')
                    struct_time_temp = time.strptime(value, "%Y:%m:%d %H:%M:%S")
                    result = time.strftime("%Y%m%d_%H%M%S", struct_time_temp)
                    return result
    except:
        print(f'\n**[Error] Cannot get EXIF_taken_time of {f}.')
        return False

## EXIF 정보 얻을 수 없을 때, 대신 "수정한 날짜" 정보를 읽는 함수
def get_modified_date(f):
    try:
        timestamp = os.path.getmtime(f)
        modified_time = time.ctime(timestamp)
        ## 아래 "%a %b ~~" 이 형식내용은 python문법이라 변경해선 안된다.
        struct_time_temp = time.strptime(modified_time, "%a %b %d %H:%M:%S %Y")
        ## 아래 "%Y%m~~" 이 부분은 사용자정의 가능하다. 이 형식으로 파일이름이 rename된다.
        result = time.strftime("%Y%m%d_%H%M%S", struct_time_temp)
        # print(f'{f} -> Modified_time : {result}')
        return result
    except:
        return None

def file_rename(f, f_type, root_dir):
    f_exif = get_photo_taken_date(f)

    if f_exif:
        print(f"-- Success to receive EXIF_taken_time from {f}")
        ## 경험상 연달아 찍은 사진은 찍은날짜(수정한 날짜)가 시/분/초가 동일하게 나와서, 파일이름중복에러로 except걸린다. 따라서 이 경우엔 초단위에 1sec를 추가하여 rename시킨다.
        for i in range(100):
            try:
                new_f_name = root_dir + '\\' + f_exif + f_type
                os.rename(f, new_f_name)
                print(f'{f} -> {new_f_name} Converted.')
                break

            except:
                print('-- Duplicate file name found(related to continuous shooting)')
                print(f'Previous new file name [{i + 1}] : {f_exif + f_type}')
                temp = int(f_exif[-1:])
                temp += 1
                f_exif = f_exif[:-1] + str(temp)
                print(f'Converted new file name [{i + 1}] : {f_exif + f_type}')

    else:
        print(f'Try to get modified_date instead..')
        f_modified_time = get_modified_date(f)

        if f_modified_time:
            for i in range(100):
                try:
                    new_f_name = root_dir + '\\' + f_modified_time + f_type
                    os.rename(f, new_f_name)
                    print(f'{f} -> {new_f_name} Converted.')
                    break

                except:
                    print('-- Duplicate file name found(related to continuous shooting)')
                    print(f'Previous new file name [{i+1}] : {f_modified_time + f_type}')
                    temp = int(f_modified_time[-1:])
                    temp += 1
                    f_modified_time = f_modified_time[:-1] + str(temp)
                    print(f'Converted new file name [{i+1}] : {f_modified_time + f_type}')

        else:
            failed_files.append(f)
            print(f'\n**[Error] Cannot get modified_time of {f}.')


def main():
    gui = GUI()
    root_dir = gui.iphone_photo_folder_path()
    files = get_image_path(root_dir)

    for f in files:
        f_type = os.path.splitext(os.path.basename(f))[1]   ## '.HEIC' or '.MOV' or etc..
        if f_type in applicable_file_type:
            file_rename(f, f_type, root_dir)
        else:
            failed_files.append(f)

    print('\n< Files failed to rename >')
    print(failed_files)
    print('\n---------- iphone photo/movie files renaming completed ----------')

if __name__ == '__main__':
    main()
