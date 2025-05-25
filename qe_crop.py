import argparse
import os
import re
import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde

def extract_convergence_errors(content):
    energy_pattern = r"Energy error\s+=\s+([-\d.E+]+)\s+Ry"
    gradient_pattern = r"Gradient error\s+=\s+([-\d.E+]+)\s+Ry/Bohr"
    energy_errors = [float(e) for e in re.findall(energy_pattern, content)]
    gradient_errors = [float(g) for g in re.findall(gradient_pattern, content)]
    return energy_errors, gradient_errors

def extract_scf_info(lines):
    cpu_pattern = re.compile(r'total cpu time spent up to now is\s+(\d+\.\d+) secs')
    scf_pattern = re.compile(r'estimated scf accuracy\s+<\s+([\d\.]+) Ry')
    scf_energy_pattern = re.compile(r'^(?!\!).*total energy\s+=\s+([-\d\.]+) Ry')
    bfgs_energy_pattern = re.compile(r'^\!\s*total energy\s+=\s+([-\d\.]+) Ry')
    iteration_pattern = re.compile(r'iteration #\s+(\d+)')

    cpu_times, scf_accuracies, iterations = [], [], []
    energy_records = []
    order = 1

    for line in lines:
        if (m := iteration_pattern.search(line)): iterations.append(int(m.group(1)))
        if (m := cpu_pattern.search(line)): cpu_times.append(float(m.group(1)))
        if (m := scf_pattern.search(line)): scf_accuracies.append(float(m.group(1)))
        if (m := bfgs_energy_pattern.search(line)):
            energy_records.append((order, float(m.group(1)), "BFGS_step")); order += 1
        elif (m := scf_energy_pattern.search(line)):
            energy_records.append((order, float(m.group(1)), "scf_step")); order += 1

    return cpu_times, scf_accuracies, energy_records, iterations
def extract_all_atomic_positions(content):
    start_str = "ATOMIC_POSITIONS (angstrom)\n"
    

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
def extract_traj(content):
    pattern = r'ATOMIC_POSITIONS.*?\n((?:\s*\w+\s+[-\d.eE+]+\s+[-\d.eE+]+\s+[-\d.eE+]+\s*\n)+)'
    matches = re.findall(pattern, content, re.DOTALL)

    frames = []
    for m in matches:
        lines = m.strip().split('\n')
        frame = []
        for line in lines:
            parts = line.split()
            if len(parts) >= 4:
                atom = parts[0]
                x, y, z = map(float, parts[1:4])
                frame.append([atom, x, y, z])
        frames.append(frame)

    return frames

def plot_and_save(filename, energy_errors, gradient_errors, cpu_times, scf_accuracies, energy_records, output_dir, traj_frames,content):
    basename = os.path.basename(filename)
    os.makedirs(output_dir, exist_ok=True)
    # --- [1] Convergence Plot ---
    if energy_errors and gradient_errors:
        df = pd.DataFrame({'Energy Error': energy_errors, 'Gradient Error': gradient_errors})
        plt.figure(figsize=(12, 6))
        plt.subplot(1, 2, 1)
        plt.plot(df.index, df['Energy Error'], marker='o')
        plt.yscale('log'); plt.title('Energy Error'); plt.xlabel('SCF Cycle'); plt.ylabel('Error (Ry)')
        plt.subplot(1, 2, 2)
        plt.plot(df.index, df['Gradient Error'], marker='o')
        plt.yscale('log'); plt.title('Gradient Error'); plt.xlabel('SCF Cycle'); plt.ylabel('Error (Ry/Bohr)')
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, basename + "_convergence.png"))
        plt.close()

    # --- [2] CPU Time Plot ---
    if len(cpu_times) >= 2:
        cpu_diffs = [j - i for i, j in zip(cpu_times[:-1], cpu_times[1:])]
        plt.plot(range(1, len(cpu_diffs) + 1), cpu_diffs, marker='o')
        plt.title("CPU Time Difference"); plt.xlabel("Iteration"); plt.ylabel("Seconds")
        plt.grid(True, linestyle='--'); plt.tight_layout()
        plt.savefig(os.path.join(output_dir, basename + "_cpu_diff.png"))
        plt.close()

    # --- [3] SCF Accuracy Plot ---
    if scf_accuracies:
        x = list(range(1, len(scf_accuracies) + 1))
        fig, ax1 = plt.subplots()
        ax1.plot(x, scf_accuracies, color='blue'); ax1.set_ylabel("Accuracy (Ry)"); ax1.set_title("SCF Accuracy")
        ax2 = ax1.twinx()
        ax2.plot(x, scf_accuracies, color='red', linestyle='--'); ax2.set_yscale('log'); ax2.set_ylabel("Log(Accuracy)")
        plt.tight_layout()
        plt.savefig(os.path.join(output_dir, basename + "_scf_accuracy.png"))
        plt.close()

    # --- [4] Total Energy Plot ---
    scf_energies = [v for _, v, t in energy_records if t == "scf_step"]
    if scf_energies:
        plt.plot(range(1, len(scf_energies) + 1), scf_energies, marker='o')
        plt.title("SCF Energy"); plt.xlabel("Step"); plt.ylabel("Energy (Ry)")
        plt.grid(True); plt.tight_layout()
        plt.savefig(os.path.join(output_dir, basename + "_total_energy.png"))
        plt.close()

    # --- [5] SCF와 BFGS CSV 저장 ---
    scf_data = [{"energy": v} for _, v, t in energy_records if t == "scf_step"]
    if scf_data:
        pd.DataFrame(scf_data).to_csv(os.path.join(output_dir, basename + "_scf_energy.csv"), index=False)

    # BFGS 스텝에 대한 에너지 및 에러값 추출
    bfgs_pattern = re.compile(
        r"!\s*total energy\s+=\s+([-\d\.Ee+]+) Ry\s+.*?"
        r"Energy error\s+=\s+([-\d\.Ee+]+) Ry\s+.*?"
        r"Gradient error\s+=\s+([-\d\.Ee+]+) Ry/Bohr", 
        re.DOTALL
    )
    bfgs_matches = bfgs_pattern.findall(content)

    bfgs_data = [
        {
            "energy": float(e),
            "energy_error": float(ee),
            "gradient_error": float(ge)
        }
        for e, ee, ge in bfgs_matches
    ]
    if bfgs_data:
        pd.DataFrame(bfgs_data).to_csv(os.path.join(output_dir, basename + "_bfgs_energy.csv"), index=False)


    # --- [6] .trj 저장 ---
    frames = extract_all_atomic_positions(content)
    if frames:
        base_filename = "input"
        trajectory_file =os.path.join(output_dir, basename + ".xyz")
        final_frame_file =os.path.join(output_dir, basename + "_final_coordinate.xyz")

        write_xyz_trajectory(frames, trajectory_file)
        write_final_frame(frames[-1], final_frame_file)

        print(f"Multi-frame trajectory written to {trajectory_file}")
        print(f"Final frame coordinates written to {final_frame_file}")
    else:
        print(f"Error: No atomic positions found in file {content}")

def main():
    parser = argparse.ArgumentParser(description="QE 전체 분석기")
    parser.add_argument('patterns', nargs='*', help="예: **/*.out (default: **/*.out)")
    parser.add_argument('--output_dir', default="./[00]qe_results", help="그래프 및 CSV 저장 경로")
    args = parser.parse_args()

    if not args.patterns:
        print("🔍 기본 패턴 사용: **/input.out")
        args.patterns = ["**/input.out"]


    file_list = []
    for pattern in args.patterns:
        file_list.extend(glob.glob(pattern, recursive=True))

    if not file_list:
        print("📛 .out 파일을 찾을 수 없습니다.")
        return

    for filepath in file_list:
        print(f"[📄] 파일 처리 중: {filepath}")
        try:
            with open(filepath, 'r') as f:
                content = f.read()
                lines = content.splitlines()
        except Exception as e:
            print(f"[ERROR] {filepath} 읽기 실패: {e}")
            continue

        energy_errors, gradient_errors = extract_convergence_errors(content)
        cpu_times, scf_accuracies, energy_records, iterations = extract_scf_info(lines)
        traj_frames = extract_traj(content)
        curdir = os.path.abspath(os.path.curdir)
        if filepath != "input.out":
            os.chdir(filepath.replace("input.out", ""))
        plot_and_save(filepath, energy_errors, gradient_errors, cpu_times, scf_accuracies, energy_records, args.output_dir, traj_frames,content)
        os.chdir(curdir)
        print(f"✅ 완료: {filepath}")

if __name__ == "__main__":
    main()
