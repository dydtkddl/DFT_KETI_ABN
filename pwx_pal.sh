#!/bin/bash

# 입력된 인자 개수 확인
if [ $# -ne 2 ]; then
    echo "Usage: $0 <num_processes> <input_file>"
    exit 1
fi

# np 값과 파일 이름 변수 설정
np=$1
filename=$(basename -- "$2")      # 파일명 추출 (경로 제외)
filename_noext="${filename%.*}"   # 확장자 제거

# 실행 명령어 출력 및 실행
echo "Running Quantum ESPRESSO with ${np} processes and input file: ${filename_noext}.in"
nohup mpirun -np "${np}" pw.x < "${filename_noext}.in" > "${filename_noext}.out" &

echo "Process started: ${filename_noext}.out (running in background)"
