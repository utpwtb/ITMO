# 为 wrench 工具创建别名
function wrench { docker run -it --rm ryukzak/wrench:latest wrench $args }
# wrench 工具别名（自动挂载当前目录）
function wrench { 
    docker run -it --rm -v ${PWD}:/work -w /work ryukzak/wrench:latest wrench $args 
}