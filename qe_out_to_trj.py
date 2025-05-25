import sys
import os
import glob
import fnmatch

def find_all_out_files(root_dir, pattern="*.out"):
    matched_files = []
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if fnmatch.fnmatch(filename, pattern):
                matched_files.append(os.path.join(dirpath, filename))
    return matched_files

def extract_all_atomic_positions(file_path):
    start_str = "ATOMIC_POSITIONS (angstrom)\n"
    
    with open(file_path, "r") as f:
        content = f.read()

    indices = []
    start = 0

    while True:
        start = content.find(start_str, start)
        if start == -1:
            break
        start += len(start_str)

        end = content.find("\n\n", start)
        if end == -1:
            end = len(content)
        
        frame_data = content[start:end].strip()
        indices.append(frame_data)
        start = end

    return indices if indices else None

def write_xyz_trajectory(frames, output_file):
    with open(output_file, "w") as f:
        for frame in frames:
            lines = frame.split("\n")
            num_atoms = 0
            cleaned_lines = []

            for line in lines:
                split_line = line.split()
                if len(split_line) >= 4:
                    cleaned_lines.append(" ".join(split_line[:4]))
                    num_atoms += 1

            if num_atoms > 0:
                f.write(f"{num_atoms}\n")
                f.write("Frame from Quantum Espresso Output\n")
                for atom_line in cleaned_lines:
                    f.write(atom_line + "\n")

def write_final_frame(frame, output_file):
    with open(output_file, "w") as f:
        lines = frame.split("\n")
        num_atoms = 0
        cleaned_lines = []

        for line in lines:
            split_line = line.split()
            if len(split_line) >= 4:
                cleaned_lines.append(" ".join(split_line[:4]))
                num_atoms += 1

        if num_atoms > 0:
            f.write(f"{num_atoms}\n")
            f.write("Final Frame from Quantum Espresso Output\n")
            for atom_line in cleaned_lines:
                f.write(atom_line + "\n")

def main():
    if len(sys.argv) < 2:
        print("Usage: python script.py <input_root_dir_or_pattern>")
        sys.exit(1)

    input_path = sys.argv[1]

    if os.path.isdir(input_path):
        files_to_process = find_all_out_files(input_path)  # ✅ 모든 하위 .out 파일 탐색
    else:
        # glob 패턴도 지원하고 싶을 경우 fallback
        files_to_process = glob.glob(input_path, recursive=True)

    if not files_to_process:
        print(f"Error: No files found under '{input_path}'")
        sys.exit(1)
    
    for input_file in files_to_process:
        print(f"Processing file: {input_file}")
        
        frames = extract_all_atomic_positions(input_file)
        if frames:
            base_filename = os.path.splitext(input_file)[0]
            trajectory_file = base_filename + ".xyz"
            final_frame_file = base_filename + "_final_coordinate.xyz"

            write_xyz_trajectory(frames, trajectory_file)
            write_final_frame(frames[-1], final_frame_file)

            print(f"Multi-frame trajectory written to {trajectory_file}")
            print(f"Final frame coordinates written to {final_frame_file}")
        else:
            print(f"Error: No atomic positions found in file {input_file}")

if __name__ == "__main__":
    main()