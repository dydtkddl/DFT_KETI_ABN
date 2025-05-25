import os
import itertools

# 사용자 정의 파라미터 (필요에 따라 수정)
variables = {
    "ecutwfc": [30, 40, 50, 60],      # sweep 대상 (Ry)
    "ecutrho_multifly": 8,            # 실제 ecutrho = ecutwfc * ecutrho_multifly
    "degauss": 0.02,                 # (Ry)
    "conv_thr": 1.0e-6,              # (Ry)
    "mixing_beta": 0.4,
    "kpoints": "4 4 1 0 0 0"         # K-point 설정 (예: 4x4x1, slab 계산용)
}

# 스크립트가 실행되는 위치에서 템플릿 파일 찾기
script_dir = os.path.dirname(os.path.abspath(__file__))
template_filename = os.path.join(script_dir, "00base_template.in")
if not os.path.exists(template_filename):
    raise FileNotFoundError(f"Template file '{template_filename}' not found in the script directory.")

# 템플릿 파일 내용 읽기
with open(template_filename, "r", encoding="utf-8") as f:
    template_content = f.read()
print(template_content)
# # 사용자에게 기본 폴더 이름 입력 받기
# base_folder = input("생성할 기본 작업 폴더 이름을 입력하세요: ").strip()
# if not base_folder:
#     raise ValueError("기본 폴더 이름을 입력해야 합니다.")
# # 기본 폴더 생성 (현재 작업 디렉토리에)
# os.makedirs(base_folder, exist_ok=True)
# print(f"기본 작업 폴더 '{base_folder}'를 생성(또는 이미 존재)하였습니다.")

# 변수 중 리스트로 정의된 파라미터(스윕 대상) 찾기
sweep_keys = [k for k, v in variables.items() if isinstance(v, list)]

# 모든 스윕 대상 파라미터의 조합 생성 (여러 개가 있을 경우)
if sweep_keys:
    sweep_combinations = list(itertools.product(*(variables[k] for k in sweep_keys)))
else:
    sweep_combinations = [()]

# 각 조합에 대해 input 파일 생성 (기본 폴더 내부에 서브 폴더 생성)
for comb in sweep_combinations:
    # sweep 대상 변수들의 현재 조합을 딕셔너리로 생성
    current_params = {k: v for k, v in variables.items() if not isinstance(v, list)}
    for key, val in zip(sweep_keys, comb):
        current_params[key] = val

    # ecutrho 계산: ecutrho = ecutwfc * ecutrho_multifly
    if "ecutwfc" in current_params and "ecutrho_multifly" in current_params:
        current_params["ecutrho"] = current_params["ecutwfc"] * current_params["ecutrho_multifly"]

    # 템플릿 내용에서 변수 치환
    new_content = template_content
    for key, val in current_params.items():
        new_content = new_content.replace(f"{{{key}}}", str(val))

    # 출력 폴더 이름 생성:
    # 먼저 sweep 대상 파라미터들을 앞에 표기하고, 그 뒤에 나머지 스칼라 변수들을 이어서 표기합니다.
    folder_name_parts = []
    # 스윕 대상
    for key in sweep_keys:
        folder_name_parts.append(f"{key}_{current_params[key]}")
    # 나머지 (단, ecutrho_multifly는 사용하지 않음)
    for key in sorted(current_params):
        if key not in sweep_keys and key != "ecutrho_multifly":
            folder_name_parts.append(f"{key}_{current_params[key]}")
    subfolder_name = "_".join(folder_name_parts)
    # 전체 경로: 기본 폴더 아래에 생성
    full_folder_path =  subfolder_name
    # full_folder_path = os.path.join(base_folder, subfolder_name)
    os.makedirs(full_folder_path, exist_ok=True)

    # 폴더 내에 input.in 파일 생성
    output_filepath = os.path.join(full_folder_path, "input.in")
    with open(output_filepath, "w", encoding="utf-8") as out_f:
        out_f.write(new_content)

    print(f"Created input file in folder '{full_folder_path}' with parameters:")
    for key, val in current_params.items():
        print(f"  {key} = {val}")
