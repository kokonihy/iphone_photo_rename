import sys, os
import time
from tkinter import messagebox
from tkinter import filedialog
# from exif import Image    ## 사진, 동영상 찍은 날짜는 모두 '수정한 날짜'와 거의 동일하기에, 여기선 EXIF를 굳이 안쓴다.

## 변환하고자하는 원본파일의 확장자명을 여기에 사전 기입해야한다. (대소문자 구분한다)
applicable_file_type = ['.JPG', '.PNG', '.HEIC', '.MOV']

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

    print('-- Total files num : ', len(result_list))

    return result_list

def get_modified_date(f):
    try:
        timestamp = os.path.getmtime(f)
        modified_time = time.ctime(timestamp)
        ## 아래 "%a %b ~~" 이 형식내용은 python문법이라 변경해선 안된다.
        struct_time_temp = time.strptime(modified_time, "%a %b %d %H:%M:%S %Y")
        ## 아래 "%Y%m~~" 이 부분은 사용자정의 가능하다. 이 형식으로 파일이름이 rename된다.
        result = time.strftime("%Y%m%d_%H%M%S", struct_time_temp)
        # print(result)
        return result
    except:
        return None

def file_rename(f, f_type, root_dir):
    f_modified_time = get_modified_date(f)
    # print(f'{f} modified_time : {f_modified_time}')

    if f_modified_time:
        ## 경험상 연달아 찍은 사진은 찍은날짜(수정한 날짜)가 시/분/초가 동일하게 나와서, 파일이름중복에러로 except걸린다. 따라서 이 경우엔 초단위에 1sec를 추가하여 rename시킨다.
        for i in range(5):  ## 바로 위 내용을 5번 try하는 것
            try:
                new_f_name = root_dir + '\\' + f_modified_time + f_type
                # print(new_f_name)
                os.rename(f, new_f_name)
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
            print(f'** Cannot get modified_time of {f}.')

    else:
        failed_files.append(f)
        print(f'** Cannot get modified_time of {f}.')


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