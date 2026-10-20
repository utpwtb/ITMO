# 操作系统

Windows 笔记仓库只保留讲义；实验在独立的私有仓库中管理。

- **讲义 PDF：**[1](lecture/1.pdf) · [2](lecture/2.pdf) · [3](lecture/3.pdf) · [4](lecture/4.pdf)
- **[实验仓库：os-labs](https://github.com/utpwtb/os-labs)**（私有，仅授权用户可访问）
- **[实验子模块](labs)**：记录实验仓库的一个具体提交。

## 本机使用

最新实验的唯一工作目录：Debian WSL `/home/chl/os-labs/intro-exp`。

Windows 文件资源管理器打开：

```text
\\wsl.localhost\Debian\home\chl\os-labs
```

本地的“打开 WSL 实验”快捷方式也指向这个目录；快捷方式不提交到 GitHub。
日常运行从 Debian 终端进入 `cd ~/os-labs/intro-exp`，按实验仓库的学习版说明操作。
旧 `student-simple` 路径是同一目录的符号链接，不占用第二份存储。

## 仓库结构

```text
5 Operating System/
├── README.md
├── lecture/       # 四份讲义 PDF
└── labs           # Git 子模块：utpwtb/os-labs，Windows 本机不展开
```

本机保持子模块未初始化，Windows 不复制实验文件。GitHub 上点击子模块可进入独立仓库；没有访问权限的用户无法查看实验内容。
在其他机器需要下载实验时，先获得私有仓库访问权限，再在笔记仓库根目录运行：

```bash
git submodule update --init -- "5 Operating System/labs"
```

子模块固定指向一个提交，更新实验后需另外提交新的子模块指向。
旧实验、旧报告镜像、课程翻译、环境快照和历史归档按要求清理，仅保存最新 simple 实验。
