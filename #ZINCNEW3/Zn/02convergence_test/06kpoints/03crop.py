import os
import re
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.ticker as ticker 
mpl.rcParams['font.family'] = 'Malgun Gothic'  # 또는 'NanumGothic'
mpl.rcParams['axes.unicode_minus'] = False     # 마이너스 기호 깨짐 방지

def find_convergence_folders(base_dir, sweep_key):
    """
    base_dir 내의 모든 폴더 중, 폴더 이름에 sweep_key와 '_'가 포함된 폴더 목록을 반환합니다.
    예: sweep_key가 "ecutwfc"인 경우 "ecutwfc_30_conv_thr_1e-06_..." 등이 대상.
    """
    folders = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]
    conv_folders = [d for d in folders if sweep_key + "_" in d]
    return conv_folders

def extract_sweep_value(folder_name, sweep_key):
    """
    폴더 이름에서 sweep_key 뒤의 숫자 값을 추출합니다.
    예: "ecutwfc_30_conv_thr_1e-06_..."에서 sweep_key="ecutwfc" → 30.0 반환.
    """
    pattern = rf"{sweep_key}_([\d\.Ee+-]+)"
    match = re.search(pattern, folder_name)
    if match:
        try:
            return float(match.group(1))
        except ValueError:
            return None
    return None

def parse_out_file(out_filepath):
    """
    주어진 .out 파일에서 다음 형식만 추출합니다:
      - "!    total energy              =  -22151.58025964 Ry"
      - "     PWSCF        :  56m28.55s CPU  57m 3.97s WALL"
      
    여기서는 d (일), h (시), m (분), s (초)를 모두 추출하며, 분과 초에 소수점이 있는 경우도 커버합니다.
    """
    total_energy = None
    cpu_time = None

    energy_pattern = re.compile(r"!\s+total energy\s*=\s*([-+]?\d*\.?\d+)\s*Ry")
    # days, hours, minutes, seconds 각각 정수 또는 소수를 허용 (분과 초에 소수점이 포함될 수 있음)
    pwscf_pattern = re.compile(
        r"PWSCF\s*:\s*"
        r"(?:(\d+(?:\.\d+)?)d)?\s*"
        r"(?:(\d+(?:\.\d+)?)h)?\s*"
        r"(?:(\d+(?:\.\d+)?)m)?\s*"
        r"(?:(\d+(?:\.\d+)?)s)?\s*CPU"
    )

    with open(out_filepath, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if total_energy is None:
                energy_match = energy_pattern.search(line)
                if energy_match:
                    try:
                        total_energy = float(energy_match.group(1))
                    except ValueError:
                        pass

            if cpu_time is None:
                pwscf_match = pwscf_pattern.search(line)
                if pwscf_match:
                    try:
                        days = float(pwscf_match.group(1)) if pwscf_match.group(1) else 0
                        hours = float(pwscf_match.group(2)) if pwscf_match.group(2) else 0
                        minutes = float(pwscf_match.group(3)) if pwscf_match.group(3) else 0
                        seconds = float(pwscf_match.group(4)) if pwscf_match.group(4) else 0
                        cpu_time = days * 86400 + hours * 3600 + minutes * 60 + seconds
                    except ValueError:
                        pass
            if total_energy is not None and cpu_time is not None:
                break

    return total_energy, cpu_time

def main():
    base_dir = os.getcwd()  # 현재 작업 디렉토리
    # 사용자에게 convergence test 폴더가 sweep 대상인 파라미터 키를 입력받음
    sweep_key = input("Convergence test 대상 파라미터 키를 입력하세요 \n(예: \n\tecutwfc\n\tecutrho_multifly\n\tdegauss\n\tconv_thr\n\tmixing_beta\n): ").strip()
    if not sweep_key:
        print("파라미터 키를 입력해야 합니다.")
        return
    
    conv_folders = find_convergence_folders(base_dir, sweep_key)
    if not conv_folders:
        print(f"'{sweep_key}_'가 포함된 convergence test 폴더를 찾을 수 없습니다.")
        return

    sweep_values = []
    energies = []
    cpu_times = []

    # 각 폴더마다 .out 파일을 탐색하여 값을 추출
    for folder in conv_folders:
        folder_path = os.path.join(base_dir, folder)
        # 폴더 내 첫 번째 .out 파일 사용
        out_files = [f for f in os.listdir(folder_path) if f.endswith(".out")]
        if not out_files:
            print(f"폴더 '{folder}'에서 .out 파일을 찾을 수 없습니다.")
            continue
        out_filepath = os.path.join(folder_path, out_files[0])
        energy, cpu_time = parse_out_file(out_filepath)
        print(energy, cpu_time)

        if energy is None or cpu_time is None:
            print(f"폴더 '{folder}': total energy 또는 CPU time 값을 추출하지 못했습니다.")
            continue

        sweep_val = extract_sweep_value(folder, sweep_key)
        if sweep_val is None:
            print(f"폴더 '{folder}'에서 sweep 값 추출 실패.")
            continue

        sweep_values.append(sweep_val)
        energies.append(energy)
        cpu_times.append(cpu_time)
        print(f"폴더 '{folder}': {sweep_key} = {sweep_val}, total energy = {energy}, CPU time = {cpu_time}")

    if not sweep_values:
        print("유효한 데이터가 없습니다.")
        return

    # 데이터 정렬 (sweep 값 기준 오름차순)
    sorted_data = sorted(zip(sweep_values, energies, cpu_times), key=lambda x: x[0])
    sweep_values, energies, cpu_times = zip(*sorted_data)

    # x축 로그 스케일 여부를 사용자에게 묻기
    use_log = input("x축을 로그 스케일로 그리시겠습니까? (y/n): ").strip().lower() == "y"

    # 플롯 생성: 두 개 y축 (왼쪽: total energy, 오른쪽: CPU time)
    fig, ax1 = plt.subplots(figsize=(8,6))
    
    color_energy = "tab:blue"
    ax1.set_xlabel(f"{sweep_key} 값")
    ax1.set_ylabel("Total Energy (Ry)", color=color_energy)
    ax1.plot(sweep_values, energies, color=color_energy, marker="o", label="Total Energy")
    ax1.tick_params(axis="y", labelcolor=color_energy)

    # x축 로그 스케일 설정 (사용자가 선택한 경우)
    if use_log:
        ax1.set_xscale("log")

    ax1.yaxis.set_major_formatter(ticker.ScalarFormatter(useMathText=False))
    ax1.ticklabel_format(style='plain', axis='y', useOffset=False)

    ax2 = ax1.twinx()
    color_cpu = "tab:red"

    # y축 단위 자동 설정
    max_cpu_time = max(cpu_times)
    if max_cpu_time >= 3600:
        time_unit = "hr"
        cpu_times_plot = [t / 3600 for t in cpu_times]
    elif max_cpu_time >= 300:
        time_unit = "min"
        cpu_times_plot = [t / 60 for t in cpu_times]
    else:
        time_unit = "sec"
        cpu_times_plot = cpu_times

    ax2.set_ylabel(f"CPU Time ({time_unit})", color=color_cpu)
    ax2.plot(sweep_values, cpu_times_plot, color=color_cpu, marker="s", label="CPU Time")
    ax2.tick_params(axis="y", labelcolor=color_cpu)
    
    title_text = f"Convergence Test: {sweep_key} Variation"
    plt.title(title_text)
    # Total Energy 점에 값 표시 (파란색)
    for x, y in zip(sweep_values, energies):
        ax1.annotate(f"{y:.2f}", xy=(x, y), xytext=(0, 5),
                    textcoords='offset points', ha='center',
                    fontsize=9, color=color_energy)

    # CPU Time 점에 값 표시 (빨간색)
    for x, y in zip(sweep_values, cpu_times_plot):
        ax2.annotate(f"{y:.2f}", xy=(x, y), xytext=(0, 5),
                    textcoords='offset points', ha='center',
                    fontsize=9, color=color_cpu)

    fig.tight_layout()
    plot_filename = "convergence_plot.png"
    plt.savefig(plot_filename)
    plt.show()
    print(f"플롯이 '{plot_filename}'로 저장되었습니다.")

if __name__ == "__main__":
    main()
