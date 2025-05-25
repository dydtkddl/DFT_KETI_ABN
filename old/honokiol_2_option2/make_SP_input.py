import os

# ORCA 입력 템플릿 (input_template.in의 내용)
orca_template = """! wB97X-D3 def2-TZVPP TightSCF RIJCOSX SP

%pal
nprocs 28
end

%maxcore 5000

"""

xyz_file = f"honokiol_2.xyz"  # run_xx에서 xx를 추출하여 사용
inp_file = f"honokiol_2_SP.inp"

if os.path.exists(xyz_file):
    with open(xyz_file, "r") as f_xyz:
        xyz_lines = f_xyz.readlines()

    # 첫 두 줄(원자 개수 및 주석)은 제거하고 ORCA 입력 형식으로 추가
    atom_lines = xyz_lines[2:]  # 첫 두 줄 제외 (원자 좌표만 추출)

    with open(inp_file, "w") as f_inp:
        f_inp.write(orca_template)  # 템플릿 쓰기
        f_inp.write("* xyz 0 1\n")  # 전하 -1, 다중도 2 설정
        f_inp.writelines(atom_lines)  # 원자 좌표 추가
        f_inp.write("*\n")  # ORCA 입력 종료

    print(f"Generated: {inp_file}")

else:
    print(f"Skipping: {xyz_file} (file not found)")

