import os
import glob

def process_input_files():
    # 파일 경로 설정
    base_dir = os.getcwd()  # 현재 작업 디렉토리
    output_folder = os.path.join(base_dir, '[00]qe_results')

    # '00_qe_results' 폴더가 없으면 생성
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # 슈퍼셀 확장 배수 입력 받기
    x_expansion = int(input("Enter expansion factor for x (e.g. 2): "))
    y_expansion = int(input("Enter expansion factor for y (e.g. 2): "))
    z_expansion = int(input("Enter expansion factor for z (e.g. 2): "))

    # 현재 폴더에서 'input.out' 파일 찾기
    input_files = [] 
    input_files.extend(glob.glob("**/input.out", recursive=True))

    # input.out 파일 처리
    for input_file in input_files:
        print(f"Processing: {input_file}")
        output_file = os.path.join(output_folder, os.path.basename(input_file) + '_expanded.xyz')

        with open(input_file, 'r') as f:
            lines = f.readlines()

        cell_parameters = []
        atomic_positions = []
        is_cell_parameters = False
        is_atomic_positions = False

        for line in lines:
            if 'CELL_PARAMETERS' in line:
                is_cell_parameters = True
                cell_ = []
                continue
            if is_cell_parameters:
                if line.strip() == '':
                    is_cell_parameters = False
                    cell_parameters.append(cell_)
                else:
                    cell_.append(line.strip())
                continue
            if 'ATOMIC_POSITIONS' in line:
                is_atomic_positions = True
                at = []
                continue
            if is_atomic_positions:
                if line.strip() == '':
                    is_atomic_positions = False
                    atomic_positions.append(at)
                else:
                    at.append(line.strip())

        # CELL_PARAMETERS로부터 cell size 계산 및 슈퍼셀 확장
        for cell_, at in zip(cell_parameters, atomic_positions):
            cell_matrix = [list(map(float, line.split())) for line in cell_]
            a_vec, b_vec, c_vec = cell_matrix
            expanded_positions = []

            for xi in range(x_expansion):
                for yi in range(y_expansion):
                    for zi in range(z_expansion):
                        for pos in at:
                            tokens = pos.split()
                            element = tokens[0]
                            try:
                                x, y, z = map(float, tokens[1:])

                                new_x = x + xi * a_vec[0] + yi * b_vec[0] + zi * c_vec[0]
                                new_y = y + xi * a_vec[1] + yi * b_vec[1] + zi * c_vec[1]
                                new_z = z + xi * a_vec[2] + yi * b_vec[2] + zi * c_vec[2]

                                expanded_positions.append(f"{element} {new_x:.10f} {new_y:.10f} {new_z:.10f}")
                            except:
                                pass
     # 결과 파일 저장 (루프 밖에서 열기)
        with open(output_file, 'w') as f:
            frame_idx = 0
            for cell_, at in zip(cell_parameters, atomic_positions):
                cell_matrix = [list(map(float, line.split())) for line in cell_]
                a_vec, b_vec, c_vec = cell_matrix
                expanded_positions = []

                for xi in range(x_expansion):
                    for yi in range(y_expansion):
                        for zi in range(z_expansion):
                            for pos in at:
                                tokens = pos.split()
                                element = tokens[0]
                                try:
                                    x, y, z = map(float, tokens[1:])

                                    new_x = x + xi * a_vec[0] + yi * b_vec[0] + zi * c_vec[0]
                                    new_y = y + xi * a_vec[1] + yi * b_vec[1] + zi * c_vec[1]
                                    new_z = z + xi * a_vec[2] + yi * b_vec[2] + zi * c_vec[2]

                                    expanded_positions.append(f"{element} {new_x:.10f} {new_y:.10f} {new_z:.10f}")
                                except:
                                    pass

                # XYZ 형식으로 현재 frame 저장
                f.write(f"{len(expanded_positions)}\n")
                f.write(f"Frame {frame_idx} from {os.path.basename(input_file)}\n")
                for pos in expanded_positions:
                    f.write(pos + '\n')
                frame_idx += 1
        print(f"Saved expanded XYZ file: {output_file}")

    print("XYZ files with expanded supercell saved successfully.")

# 함수 호출
if __name__ == "__main__":
    process_input_files()
