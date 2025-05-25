import os
import sys
import shutil
import re

def extract_last_atomic_positions(out_path):
    with open(out_path, 'r') as f:
        content = f.read()

    # 모든 ATOMIC_POSITIONS (angstrom) 블록 찾기
    pattern = r"ATOMIC_POSITIONS \(angstrom\)\n(.*?)(?=\n\s*\n|\Z)"
    matches = re.findall(pattern, content, re.DOTALL)

    if not matches:
        raise ValueError("ATOMIC_POSITIONS (angstrom) block not found in .out file")

    last_block = matches[-1].strip()
    return "ATOMIC_POSITIONS (angstrom)\n" + last_block + "\n"

def replace_atomic_positions_in_input(input_path, new_block):
    with open(input_path, 'r') as f:
        content = f.readlines()
    count = 0
    crop_index = []
    for line in content:
        if "ATOMIC_POSITIONS" in line :
            crop_index.append(count)
        if crop_index and line.strip() == "":
            crop_index.append(count)
            break
        count +=1
    content_front = "".join(content[:crop_index[0]])
    content_mid = new_block 
    content_back = "".join(content[crop_index[1] : ])
    return content_front + content_mid + content_back

def main():
    if len(sys.argv) != 3:
        print("사용법: python script.py <기존_디렉토리> <새_디렉토리_이름>")
        sys.exit(1)

    input_dir = sys.argv[1]
    new_dir_name = sys.argv[2]

    # 파일 경로
    out_file = None
    input_file = None

    for f in os.listdir(input_dir):
        if f.endswith('input.out'):
            out_file = os.path.join(input_dir, f)
        elif f.endswith('input.in'):
            input_file = os.path.join(input_dir, f)
    print(os.listdir(input_dir))
    if not out_file or not input_file:
        print("입력 디렉토리 내에 .out 또는 .input 파일이 없습니다.")
        sys.exit(1)

    # ATOMIC_POSITIONS 블록 추출
    atomic_block = extract_last_atomic_positions(out_file)
    # 기존 input 수정
    new_input = replace_atomic_positions_in_input(input_file, atomic_block)
    print(new_input)
    # 새 디렉토리 생성 및 복사
    new_dir = os.path.join(os.getcwd(), new_dir_name)
    os.makedirs(new_dir, exist_ok=True)

    # for f in os.listdir(input_dir):
    #     full_path = os.path.join(input_dir, f)
    #     if os.path.isfile(full_path):
    #         shutil.copy(full_path, new_dir)

    # 수정된 input 파일 덮어쓰기
    new_input_path = os.path.join(new_dir, os.path.basename(input_file))
    with open(new_input_path, 'w') as f:
        f.write(new_input)

    print(f"새 디렉토리 '{new_dir_name}' 생성 완료. input 파일 수정 완료.")

if __name__ == "__main__":
    main()
