#!/bin/bash
# 04run_with_multiple_nodes.sh

BASE_DIR=$(pwd)

CPU_NODES=${1:-33}

#NODES=("psid00" "psid01" "psid02" "psid03" "psid04" "psid05" "psid06" "psid07" "psid08" "psid09" "psid10")
NODES=("psid00" "psid01" "psid02" "psid03" "psid05")
DIRS=( 
    # Zn002/02_Zn002_Topsite_Upright/try01
    Zn002/04_Zn002_Lean/try02
    Zn100/02_Zn100_Topsite_Upright/try02
    Zn100/04_Zn100_Lean/try02
    Zn101/02_Zn101_Topsite_Upright/try02
    Zn101/04_Zn101_Lean/try02
)

echo "다음 디렉토리에서 작업을 실행합니다:"
for d in "${DIRS[@]}"; do
    echo "  $d"
done

echo "사용할 CPU 노드 수: $CPU_NODES"
echo "사용할 클러스터 노드: ${NODES[@]}"

read -p "진짜 돌리시겠습니까? (y/n): " answer
if [[ "$answer" != "y" && "$answer" != "Y" ]]; then
    echo "실행 취소"
    exit 1
fi

node_index=0
for d in "${DIRS[@]}"; do
    node=${NODES[$node_index]}
    echo "노드 $node 에서 디렉토리 $d 실행"

    ssh "$node" "cd \"${BASE_DIR}/${d}\" && sh \${QE}pwx_pal.sh ${CPU_NODES} input.in" &
    
    node_index=$(( (node_index + 1) % ${#NODES[@]} ))
done

wait
echo "모든 작업이 완료되었습니다."

