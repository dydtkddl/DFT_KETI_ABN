import os
from glob import glob
import argparse
import warnings
warnings.filterwarnings('ignore', message='.*OVITO.*PyPI')
def collect_xyz_csv_files(base_dir=".", folders=None):
    if folders:
        expanded_folders = []
        for pattern in folders:
            matched = glob(pattern)
            expanded_folders.extend([d for d in matched if os.path.isdir(d)]
                                    )
            print(expanded_folders)
        xyzpaths = [os.path.join(f, "[00]qe_results","input.out.xyz") for f in expanded_folders if os.path.exists(os.path.join(f, "[00]qe_results","input.out.xyz"))]
        csvpaths = [os.path.join(f, "[00]qe_results","input.out_bfgs_energy.csv") for f in expanded_folders if os.path.exists(os.path.join(f, "[00]qe_results","input.out.xyz"))]
    else:
        xyzpaths = sorted(glob(os.path.join(base_dir, "**", "input.out.xyz"), recursive=True))
        csvpaths =sorted(glob(os.path.join(base_dir, "**", "input.out_bfgs_energy.csv"), recursive=True))
    return xyzpaths, csvpaths

import pprint
def is_valid_xyz(content):
    # lines = content.strip().splitlines()
    # pprint.pprint(lines)
    # try:
    #     n_atoms = int(lines[0])
    #     print(len(lines))
    #     print(  n_atoms + 2)
    #     return len(lines) == n_atoms + 2
    
    # except:
    return True

def concatenate_xyz_files(xyz_paths, output_file):
    with open(output_file, 'w') as outfile:
        valid_count = 0
        for path in xyz_paths:
            with open(path, 'r') as infile:
                blocks = infile.read().strip().split('\n\n')
                for block in blocks:
                    if is_valid_xyz(block):
                        outfile.write(block.strip() + '\n')
                        valid_count += 1
        print(f"[✅] 총 {valid_count}개 프레임을 이어붙여 '{output_file}'로 저장 완료.")
import pandas as pd
import matplotlib.pyplot as plt

def concatenate_csv_files(csv_paths, output_file):
    dfs = []
    valid_count = 0
    for path in csv_paths:
        dfs.append(pd.read_csv(path))
        valid_count += 1

    # CSV 이어붙이기
    df = pd.concat(dfs, axis=0).reset_index()
    df.to_csv(output_file)

    # Plot 그리기
    fig, axs = plt.subplots(3, 1, figsize=(10, 8), sharex=True)
    fig.suptitle("Energy and Error Metrics over Index", fontsize=14)

    axs[0].plot(range(len(df["index"])), df["energy"], marker='o', linestyle='-', color='steelblue', label='Energy')
    axs[0].set_ylabel("Energy")
    axs[0].legend()
    axs[0].grid(True)

    axs[1].plot(range(len(df["index"])), df["energy_error"], marker='s', linestyle='-', color='orange', label='Energy Error')
    axs[1].set_ylabel("Energy Error")
    axs[1].legend()
    axs[1].grid(True)

    axs[2].plot(range(len(df["index"])), df["gradient_error"], marker='^', linestyle='-', color='green', label='Gradient Error')
    axs[2].set_xlabel("Index")
    axs[2].set_ylabel("Gradient Error")
    axs[2].legend()
    axs[2].grid(True)

    plt.tight_layout(rect=[0, 0, 1, 0.96])  # suptitle과의 간격 조정
    plt.savefig(output_file.replace(".csv", ".png"))

    print(f"[✅] 총 {valid_count}개 CSV을 이어붙여 '{output_file}'로 저장 완료.")
from matplotlib import animation

def generate_progress_plot(df, output_gif, fps=30):
    print("[📈] 진행도 : 그래프 애니메이션 생성 시작...")

    fig, axs = plt.subplots(3, 1, figsize=(10, 6), sharex=True)
    fig.suptitle("Energy and Error Metrics over Time", fontsize=14)

    x = range(len(df))
    axs[0].plot(x, df["energy"], color='steelblue', label='Energy')
    axs[1].plot(x, df["energy_error"], color='orange', label='Energy Error')
    axs[2].plot(x, df["gradient_error"], color='green', label='Gradient Error')
    for ax in axs:
        ax.grid(True)
        ax.legend()

    # 초기 수직선 (움직이게 만들기 위해 리스트로 넣어줌)
    lines = [ax.axvline(0, color='red', linestyle='--') for ax in axs]

    def update(frame):
        if frame % 10 == 0 or frame == len(df) - 1:
            print(f"    ▶ 진행도 : 프레임 {frame + 1}/{len(df)} 처리 중...")
        for line in lines:
            line.set_xdata([frame])
        return lines

    ani = animation.FuncAnimation(fig, update, frames=len(df), blit=True, interval=1000/fps)
    ani.save(output_gif, writer='pillow', fps=fps)
    plt.close(fig)

    print(f"[✅] 진행도 애니메이션 '{output_gif}' 저장 완료.")


from PIL import Image

def stack_gifs_vertically(gif_paths, plot_gif_path, output_gif):
    print(f"[🔧] GIF 병합 시작: 상단 {len(gif_paths)}개 + 하단 plot GIF ➜ {output_gif}")
    # OVITO GIFs 열기
    imgs = [Image.open(p) for p in gif_paths]
    plot_frames = Image.open(plot_gif_path)

    top_width = sum(img.width for img in imgs)  # 상단 전체 너비
    top_height = imgs[0].height  # 동일 높이 가정
    bottom_width = plot_frames.width  # 동일 높이 가정
    total_frames = plot_frames.n_frames

    print(f"  - 총 프레임 수: {total_frames}")
    # print(f"  - 상단 너비 합계: {top_width}px | 상단 높이: {top_height}px")

    plot_resized = []

    from tqdm import tqdm

    for i in tqdm(range(total_frames), desc="▶ 프레임 처리 진행"):
        plot_frames.seek(i)
        plot_frame = plot_frames.copy().convert("RGB")
        new_height = int(plot_frame.height * top_width / bottom_width)
        plot_frame_resized = plot_frame.resize((top_width, new_height), Image.Resampling.LANCZOS)
        combined = Image.new('RGB', (top_width, top_height + new_height))

        for j, img in enumerate(imgs):
            img.seek(i)
            combined.paste(img.copy(), (j * img.width, 0))


        combined.paste(plot_frame_resized, (0, top_height))
        plot_resized.append(combined)
    print("## 프레임 저장중... (조금 시간 걸림)")
    plot_resized[0].save(
        output_gif, save_all=True, append_images=plot_resized[1:], duration=1000/30, loop=0
    )

    print(f"[✅] GIF 병합 완료! 최종 결과 저장: {output_gif}")

def render_with_ovito(xyz_file,prefix,OUTPUT_PATH):
    from ovito.io import import_file
    from ovito.vis import Viewport
    from ovito.pipeline import StaticSource
    import warnings
    warnings.filterwarnings('ignore', message='.*OVITO.*PyPI')

    print(f"[📊] OVITO로 애니메이션 렌더링 시작...")

    views = {
        # "perspective": Viewport.Type.Perspective,
        # "Ortho": Viewport.Type.Ortho,
        "Top": Viewport.Type.Top,
        # "Bottom": Viewport.Type.Bottom,
        "Front": Viewport.Type.Front,
        # "Back": Viewport.Type.Back,
        "Left": Viewport.Type.Left,
        "Right": Viewport.Type.Right,
    }
    pipeline = import_file(xyz_file, multiple_frames=True)
    pipeline.add_to_scene()  # ✔ 반드시 추가해야 scene에서 렌더링됨
    num_frames = pipeline.source.num_frames

    for name, view_type in views.items():
        vp = Viewport(type=view_type)
        vp.zoom_all()
        gif_name = f"{OUTPUT_PATH}{prefix}_animation_{name}.gif"
        vp.render_anim(
            filename=gif_name,
            size=(600, 480),
            fps=30,
            background=(1, 1, 1),  # 배경 제거는 png로 렌더링한 뒤 후처리
            range=(0, num_frames - 1)
        )
    
        print(f"  - [{name}] ➜ {gif_name}")

    print("[✅] 모든 View 애니메이션 렌더링 완료.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="input.out.xyz 파일 병합 및 OVITO 애니메이션 자동화")
    parser.add_argument("--folders", nargs='+', help="특정 하위 폴더 리스트 (예: try01 try02)")
    parser.add_argument("--gif", default = "no")
    parser.add_argument("--prefix", default = "")
    parser.add_argument("--output_dir", default = "./")
    parser.add_argument("--start_dir" , default = "./")
    args = parser.parse_args()
    prefix = args.prefix
    start_dir = args.start_dir 

    os.chdir(start_dir)
    OUTPUT_PATH = args.output_dir
    output_file_xyz = f"{OUTPUT_PATH}{prefix}_integrated.xyz"
    output_file_csv = f"{OUTPUT_PATH}{prefix}_integrated.bfgs.csv"
    base_dir = "."

    xyz_files, csvfiles = collect_xyz_csv_files(base_dir, args.folders)
    if not xyz_files:
        print("📛 input.out.xyz 파일을 찾을 수 없습니다.")
    else:
        concatenate_xyz_files(xyz_files, output_file_xyz)
        concatenate_csv_files(csvfiles, output_file_csv)
        if args.gif == "yes" or args.gif == "y":
            render_with_ovito(output_file_xyz,prefix,OUTPUT_PATH)
            generate_progress_plot(pd.read_csv(output_file_csv), f"{OUTPUT_PATH}{prefix}_##progress_plot.gif", fps=30)
            stack_gifs_vertically(
                [f"{OUTPUT_PATH}{prefix}_animation_Left.gif", f"{OUTPUT_PATH}{prefix}_animation_Right.gif", f"{OUTPUT_PATH}{prefix}_animation_Front.gif"],
                f"{OUTPUT_PATH}{prefix}_##progress_plot.gif",
                f"{OUTPUT_PATH}{prefix}_##combined_final.gif"
            )
            print(f"[🎬] 최종 {prefix}_##combined_final.gif 생성 완료!")
        ## 여기에서 그린 figure를  그릴때 이전에 만든 .gif를 합친 gif를 또 만들거야
        ## animation_Left.gif, animation_Right.gif, animation_Front.gif 이 세개를 .gif의 위쪽 섹션을 세등분 한 공간에 각각 배치할거야
        ## 사용한 fps = 30인데, 이 속도에 맞춰서 plt.axvline이 1씩증가하게 만들어서 progress가 보이게 동적으로 만들거야
        ## concatenate_csv_files함수에서 기존에 .png를 만들던것을 .gif를 만들게 수정해야해
