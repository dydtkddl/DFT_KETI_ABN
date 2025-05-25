#!/bin/bash
# 04run_with_multiple_nodes.sh

# 현재 스크립트가 실행된 디렉토리를 기준 디렉토리로 설정
BASE_DIR=$(pwd)

# 사용자가 원하는 CPU 노드 수 (기본값: 33). 인자로 전달할 수 있음.
CPU_NODES=${1:-33}

# 사용할 클러스터 노드 목록 (빈 노드 번호를 명시적으로 입력)
#NODES=("psid00" "psid01" "psid02" "psid03" "psid04" "psid05" "psid06" "psid07" "psid08" "psid09" "psid10")
NODES=("psid00" "psid01" "psid02" "psid03" "psid04" "psid05" "psid06")
# 현재 BASE_DIR 내에서 실행할 대상 디렉토리 목록 (예: mixing_beta_ 로 시작하는 폴더들)
# 따옴표로 감싸서 공백 포함 전체 이름을 보존합니다.
DIRS=( "mixing_beta_"* )

echo "다음 디렉토리에서 작업을 실행합니다:"
for d in "${DIRS[@]}"; do
    echo "  $d"
done

echo "사용할 CPU 노드 수: $CPU_NODES"
echo "사용할 클러스터 노드: ${NODES[@]}"

# 최종 실행 전 사용자 확인
read -p "진짜 돌리시겠습니까? (y/n): " answer
if [[ "$answer" != "y" && "$answer" != "Y" ]]; then
    echo "실행 취소"
    exit 1
fi

# 각 디렉토리마다 클러스터 노드로 ssh 접속해 작업 실행 (노드 목록을 라운드로빈 방식으로 사용)
node_index=0
for d in "${DIRS[@]}"; do
    node=${NODES[$node_index]}
    echo "노드 $node 에서 디렉토리 $d 실행"

    # SSH 커맨드 내에서 BASE_DIR과 $d에 공백이 포함되어 있을 수 있으므로, 적절히 따옴표를 사용합니다.
    ssh "$node" "cd \"${BASE_DIR}/${d}\" && sh \${QE}pwx_pal.sh ${CPU_NODES} input.in" &
    
    # 다음 노드로 순환 (노드 목록의 길이만큼 반복)
    node_index=$(( (node_index + 1) % ${#NODES[@]} ))
done

# 모든 백그라운드 작업이 완료될 때까지 대기
wait
echo "모든 작업이 완료되었습니다."

