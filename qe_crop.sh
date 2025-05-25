#!/bin/bash

# 현재 실행 중인 sh 파일의 절대 경로 가져오기
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# qe_out_to_trj.py 실행
python "$SCRIPT_DIR/qe_out_to_trj.py" ./*.out
python "$SCRIPT_DIR/qe_out_to_trj.py" ./**/*.out
python "$SCRIPT_DIR/qe_out_to_trj.py" ./**/**/*.out

# qe_plot_convergence.py 실행
python "$SCRIPT_DIR/qe_plot_convergence.py" ./*.out
python "$SCRIPT_DIR/qe_plot_convergence.py" ./**/*.out
python "$SCRIPT_DIR/qe_plot_convergence.py" ./**/**/*.out

# qe_scf_plot.py 실행
python "$SCRIPT_DIR/qe_scf_plot.py" ./*.out
python "$SCRIPT_DIR/qe_scf_plot.py" ./**/*.out
python "$SCRIPT_DIR/qe_scf_plot.py" ./**/**/*.out
