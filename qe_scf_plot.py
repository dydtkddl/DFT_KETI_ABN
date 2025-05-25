import argparse
import re
import glob
import matplotlib.pyplot as plt
import os
import pandas as pd
import numpy as np

# Argument parser 설정
parser = argparse.ArgumentParser(description='Parse log files and plot CPU time differences, SCF accuracy, and total energy.')
parser.add_argument('logfiles', type=str, nargs='+', help='Path to the log files (supports glob patterns like *.out or ./**/*.out)')
parser.add_argument('--output_dir', type=str, default='.', help='Output directory for the plots')
args = parser.parse_args()

# glob을 사용하여 다중 파일 처리
logfile_paths = []
for pattern in args.logfiles:
    logfile_paths.extend(glob.glob(pattern, recursive=True))

# 정규 표현식 패턴들
cpu_time_pattern = re.compile(r'total cpu time spent up to now is\s+(\d+\.\d+) secs')
# scf_energy_pattern는 "total energy = ... Ry"를 매칭하지만, 느낌표가 있으면 배제
scf_energy_pattern = re.compile(r'^(?!\!).*total energy\s+=\s+([-\d\.]+) Ry')
# bfgs_energy_pattern는 느낌표로 시작하는 구문을 매칭
bfgs_energy_pattern = re.compile(r'^\!\s*total energy\s+=\s+([-\d\.]+) Ry')
scf_pattern = re.compile(r'estimated scf accuracy\s+<\s+([\d\.]+) Ry')
iteration_pattern = re.compile(r'iteration #\s+(\d+)')

for logfile in logfile_paths:
    print(f"Processing file: {logfile}")
    
    # 출력 디렉토리 설정 (명시적 입력 없을 경우 해당 로그파일 경로 기준)
    if args.output_dir == '.':
        output_dir = os.path.dirname(os.path.abspath(logfile))
    else:
        output_dir = os.path.abspath(args.output_dir)
    os.makedirs(output_dir, exist_ok=True)  # 출력 디렉토리 생성

    with open(logfile, 'r') as file:
        log_content = file.readlines()

    cpu_times, scf_accuracies, iterations = [], [], []
    # 기존 에너지 리스트 대신, 에너지 레코드를 순서대로 저장할 리스트 (order, energy_value, step_type)
    energy_records = []
    order_counter = 1  # 에너지 레코드의 순서를 나타내는 카운터

    for line in log_content:
        if (iter_match := iteration_pattern.search(line)):
            iterations.append(int(iter_match.group(1)))
        if (cpu_match := cpu_time_pattern.search(line)):
            cpu_times.append(float(cpu_match.group(1)))
        if (scf_match := scf_pattern.search(line)):
            scf_accuracies.append(float(scf_match.group(1)))
        # 에너지 구문 처리: 먼저 느낌표로 시작하는 구문(BFGS), 그 외(scF)
        bfgs_match = bfgs_energy_pattern.search(line)
        if bfgs_match:
            energy_records.append((order_counter, float(bfgs_match.group(1)), "BFGS_step"))
            order_counter += 1
            continue  # BFGS 구문이면 scf_energy_pattern은 검사하지 않음
        scf_energy_match = scf_energy_pattern.search(line)
        if scf_energy_match:
            energy_records.append((order_counter, float(scf_energy_match.group(1)), "scf_step"))
            order_counter += 1

    if len(cpu_times) < 2:
        print(f"Insufficient data in file {logfile}, skipping...")
        continue

    # CPU time 차이 계산
    cpu_time_diffs = [j - i for i, j in zip(cpu_times[:-1], cpu_times[1:])]
    iter_steps = list(range(1, len(cpu_time_diffs) + 1))
    scf_steps = list(range(1, len(scf_accuracies) + 1))
    # 에너지 그래프에 사용할 scf 에너지 리스트 (예: scf_step만 따로 사용)
    scf_energies = [energy for _, energy, typ in energy_records if typ == "scf_step"]
    energy_steps = list(range(1, len(scf_energies) + 1))

    # CPU Time 그래프
    plt.figure(figsize=(10, 6))
    plt.plot(iter_steps, cpu_time_diffs, marker='o', linestyle='-')
    plt.xlabel('Iteration Number')
    plt.ylabel('CPU Time Difference (secs)')
    plt.title(f'CPU Time Differences ({os.path.basename(logfile)})')
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, f"{os.path.basename(logfile)}_cpu_time_graph.png"))
    plt.close()

    # SCF Accuracy 그래프 (Real, Log 이중축)
    fig, ax1 = plt.subplots(figsize=(10, 6))
    color1 = 'tab:blue'
    ax1.set_xlabel('Iteration Step')
    ax1.set_ylabel('Estimated SCF Accuracy (Ry, Real scale)', color=color1)
    ax1.plot(scf_steps, scf_accuracies, marker='o', color=color1, label='Real scale')
    ax1.tick_params(axis='y', labelcolor=color1)
    ax1.grid(True, linestyle='--', alpha=0.5)

    ax2 = ax1.twinx()
    color2 = 'tab:red'
    ax2.set_ylabel('Estimated SCF Accuracy (Ry, Log scale)', color=color2)
    ax2.plot(scf_steps, scf_accuracies, marker='s', linestyle='--', color=color2, label='Log scale')
    ax2.set_yscale('log')
    ax2.tick_params(axis='y', labelcolor=color2)

    plt.title(f'Estimated SCF Accuracy ({os.path.basename(logfile)})')
    fig.tight_layout()
    plt.savefig(os.path.join(output_dir, f"{os.path.basename(logfile)}_scf_accuracy_graph.png"))
    plt.close()

    # Total Energy 그래프 (Real scale + Pseudo-log scale)
    fig, ax1 = plt.subplots(figsize=(10, 6))
    color1 = 'tab:blue'
    ax1.set_xlabel('Iteration Step')
    ax1.set_ylabel('Total Energy (Ry, Real scale)', color=color1)
    # 여기서는 scf 에너지만 사용하여 플롯 (또는 필요에 따라 energy_records 전체를 이용할 수 있음)
    ax1.plot(energy_steps, scf_energies, marker='o', color=color1)
    ax1.tick_params(axis='y', labelcolor=color1)
    ax1.grid(True, linestyle='--', alpha=0.5)
    plt.title(f'Total Energy ({os.path.basename(logfile)})')
    fig.tight_layout()
    plt.savefig(os.path.join(output_dir, f"{os.path.basename(logfile)}_total_energy_graph.png"))
    plt.close()

    # CSV 저장: 에너지 레코드를 순서대로 저장 (두번째 열 이름은 레코드 타입에 따라 구분)

    records = []
    for order, value, step_type in energy_records:
        records.append({"energy": value, "step_type": step_type})
    energy_df = pd.DataFrame(records)
    csv_path = os.path.join(output_dir, f"{os.path.basename(logfile)}_total_energy.csv")
    energy_df.to_csv(csv_path, index=False)
    print(csv_path)
    print(f"Graphs and CSV saved for {logfile}")
