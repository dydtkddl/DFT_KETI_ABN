import os
import shutil

def main():
    # 1. 사용자로부터 폴더 이름 입력받기
    target_folder_name = input("생성할 폴더 이름을 입력하세요: ").strip()
    if not target_folder_name:
        print("폴더 이름을 입력해야 합니다.")
        return

    # 2. 현재 사용자의 작업 디렉터리 (스크립트 실행 위치가 아닌, 현재 working directory)
    current_working_dir = os.getcwd()
    target_folder_path = os.path.join(current_working_dir, target_folder_name)
    
    # 3. 폴더가 이미 존재하면 안내, 없으면 생성
    if not os.path.exists(target_folder_path):
        os.makedirs(target_folder_path)
        print(f"폴더 '{target_folder_path}'를 생성했습니다.")
    else:
        print(f"폴더 '{target_folder_path}'가 이미 존재합니다.")

    # 4. 스크립트(02make_convergence_test_folders.py)의 위치를 기준으로 복사할 파일들이 있는 디렉터리 결정
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 복사할 파일 리스트 (필요에 따라 수정)
    files_to_copy = ["00base_template.in", "01convergence_test.py", "03crop.py", "04run_with_multiple_nodes.sh"]
    # 5. 각 파일을 target 폴더로 복사
    for filename in files_to_copy:
        src_path = os.path.join(script_dir, filename)
        dst_path = os.path.join(target_folder_path, filename)
        if os.path.exists(src_path):
            shutil.copy2(src_path, dst_path)
            print(f"'{filename}' 파일을 '{target_folder_path}'로 복사했습니다.")
        else:
            print(f"경고: '{filename}' 파일을 찾을 수 없습니다. (원본: {src_path})")

if __name__ == "__main__":
    main()
