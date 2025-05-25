import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import os
import argparse
import glob
import re
def extract_errors(output_content):
    """
    Extract energy and gradient errors from the provided output content.
    """
    # Regular expression to find Energy and Gradient errors
    energy_pattern = r"Energy error\s+=\s+([-\d.E+]+)\s+Ry"
    gradient_pattern = r"Gradient error\s+=\s+([-\d.E+]+)\s+Ry/Bohr"
    
    energy_errors = re.findall(energy_pattern, output_content)
    gradient_errors = re.findall(gradient_pattern, output_content)
    
    # Convert to float for plotting
    energy_errors = [float(e) for e in energy_errors]
    gradient_errors = [float(g) for g in gradient_errors]
    
    return energy_errors, gradient_errors

def plot_convergence(energy_errors, gradient_errors, filename="convergence_plot.png"):
    """
    Generate the convergence plots for Energy and Gradient errors with logarithmic scale.
    """
    # Create a DataFrame for easy plotting
    df = pd.DataFrame({
        'Energy Error': energy_errors,
        'Gradient Error': gradient_errors
    })

    # Set the size of the plots
    plt.figure(figsize=(12, 6))
    
    # Create the first plot for Energy Error
    plt.subplot(1, 2, 1)
    sns.lineplot(data=df, x=df.index, y='Energy Error', marker='o')
    plt.yscale('log')  # Set y-axis to log scale
    plt.title('Energy Error Convergence (Log Scale)')
    plt.xlabel('SCF Cycle')
    plt.ylabel('Energy Error (Ry)')
    
    # Create the second plot for Gradient Error
    plt.subplot(1, 2, 2)
    sns.lineplot(data=df, x=df.index, y='Gradient Error', marker='o')
    plt.yscale('log')  # Set y-axis to log scale
    plt.title('Gradient Error Convergence (Log Scale)')
    plt.xlabel('SCF Cycle')
    plt.ylabel('Gradient Error (Ry/Bohr)')
    
    # Save the plot as a PNG file
    plt.tight_layout()
    print(os.path.basename(filename))
    plt.savefig(filename)
    print(f"[INFO] {filename} 저장 완료")
    plt.close()

def main():
    """
    Main function to process the output files, extract errors, and generate plots.
    """
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Process the output log files and generate convergence plots for Energy and Gradient errors.")
    parser.add_argument("output_files", help="The path to the output file(s) to process (use '*' for multiple files)", nargs='+')
    
    # Parse command line arguments
    args = parser.parse_args()

    # Expand wildcard pattern using glob
    files_to_process = []
    for pattern in args.output_files:
        files_to_process.extend(glob.glob(pattern))

    if not files_to_process:
        print("[ERROR] No matching files found.")
        return

    # Process each file
    for output_filename in files_to_process:
        print(f"[INFO] '{output_filename}' 파일 읽는 중...")
        try:
            with open(output_filename, 'r') as file:
                output_content = file.read()
        except FileNotFoundError:
            print(f"[ERROR] 파일 '{output_filename}'을(를) 찾을 수 없습니다. 파일 경로를 확인해주세요.")
            continue

        # Extract energy and gradient errors from the content
        print("[INFO] Energy 및 Gradient Error 수집 완료.")
        energy_errors, gradient_errors = extract_errors(output_content)

        if not energy_errors or not gradient_errors:
            print(f"[WARNING] Energy 및 Gradient Error를 찾을 수 없습니다. 로그 파일 형식을 확인하세요: {output_filename}")
            continue
        
        # Modify filename to save as PNG
        save_filename = output_filename.replace('.out', '.png')
        
        # Generate the convergence plots and save the file
        print(f"[INFO] '{output_filename}'의 데이터를 바탕으로 수렴 그래프를 생성 중...")
        plot_convergence(energy_errors, gradient_errors, filename=save_filename)
        print(f"[INFO] 작업이 완료되었습니다. 결과는 '{save_filename}'에 저장되었습니다.")

if __name__ == "__main__":
    main()
