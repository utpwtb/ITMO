# BPF / XDP

> 中文全译：[原文](https://github.com/secs-dev/os-course/blob/dee17bc418979ecbae3b45db74cdc1494bdc9bb1/lab/bpf-xdp/README.md)。

本实验通过 [XDP](https://docs.ebpf.io/linux/program-type/BPF_PROG_TYPE_XDP/) 学习 [eBPF](https://ebpf.io/what-is-ebpf/)。

先从最简单 XDP 过滤器开始，加载到内核运行，再实现、测试简单 RPS 限速器。从直接使用 C 与 [bpf 系统调用](https://man7.org/linux/man-pages/man2/bpf.2.html)，逐步转向 [libbpf](https://docs.kernel.org/bpf/libbpf/libbpf_overview.html)。

## 准备

Ubuntu 安装以下包：

```bash
sudo apt install clang llvm gcc
```

确认 `clang` 支持 `bpf` 编译目标：

```bash
clang --print-targets | grep bpf
```

编译需要系统头文件：

```bash
ls /usr/include/$(gcc -print-multiarch)
```

## 第一个 XDP 过滤器

在 `pass.bpf.c` 中编写以下过滤器：

```c
#include <linux/bpf.h>

__attribute__((section("xdp"), used))
enum xdp_action pass(struct xdp_md *ctx) {
  (void)ctx;
  return XDP_PASS;
}
```

输入是 [struct xdp_md](https://github.com/torvalds/linux/blob/cf72cbb39da84b6f02f90c07f33b102fc10b16f0/include/uapi/linux/bpf.h#L6662-L6664)，返回 [enum xdp_action](https://github.com/torvalds/linux/blob/cf72cbb39da84b6f02f90c07f33b102fc10b16f0/include/uapi/linux/bpf.h#L6651C1-L6657)。

编译：

```bash
clang -target bpf -I/usr/include/$(gcc -print-multiarch) -c pass.bpf.c -o pass.bpf.o
```

查看字节码：

```bash
llvm-objdump --disassemble pass.bpf.o
# Disassembly of section xdp:
#0000000000000000 <pass>:
#       0:	7b 1a f8 ff 00 00 00 00	*(u64 *)(r10 - 0x8) = r1
#       1:	b7 00 00 00 02 00 00 00	r0 = 0x2
#       2:	95 00 00 00 00 00 00 00	exit
```

启用优化再编译，比较字节码。

可以看到 BPF 程序只有几十字节，但对象文件明显更大：

```bash
stat -c %s pass.bpf.o
```

还包含哪些信息？为什么需要它们？提示：研究 `llvm-readelf`。

每条 BPF 指令占 8 字节，用 [struct bpf_insn](https://github.com/torvalds/linux/blob/cf72cbb39da84b6f02f90c07f33b102fc10b16f0/include/uapi/linux/bpf.h#L80-L86) 表示。

先用 [BPF_PROG_LOAD](https://github.com/torvalds/linux/blob/cf72cbb39da84b6f02f90c07f33b102fc10b16f0/include/uapi/linux/bpf.h#L261-L274) 把程序作为资源加载到内核。

命令是 `bpf` 系统调用的第一个参数，随后为 [union bpf_attr](https://github.com/torvalds/linux/blob/cf72cbb39da84b6f02f90c07f33b102fc10b16f0/include/uapi/linux/bpf.h#L1527C1-L1527C15)，这里使用其 [BPF_PROG_LOAD 对应成员](https://github.com/torvalds/linux/blob/cf72cbb39da84b6f02f90c07f33b102fc10b16f0/include/uapi/linux/bpf.h#L1608-L1672)。

从对象文件取得所需字节：

```bash
llvm-objcopy --dump-section xdp=/dev/stdout pass.bpf.o | hexdump -C
```

随后可按类似方式加载：

```c
const char license[] = "GPL";

union bpf_attr attr = {};
attr.prog_type = BPF_PROG_TYPE_XDP;
attr.insn_cnt = count;
attr.insns = (__u64)insns;
attr.license = (__u64)license;

int fd = syscall(SYS_bpf, BPF_PROG_LOAD, &attr, sizeof(union bpf_attr));
```

用 `BPF_PROG_TEST_RUN` 测试。

实现并运行从文件加载过滤器、测试它的程序，保存为 `load_xdp.c`。

## 创建虚拟网络接口

创建具有独立网络表的 network namespace：

```bash
sudo ip netns add xdp-ns
```

创建相连的虚拟 Ethernet 接口对：

```bash
sudo ip link add xdp-host type veth peer name xdp-peer
```

把 veth 的另一端移入 `xdp-ns`：

```bash
sudo ip link set xdp-peer netns xdp-ns
```

设置地址：

```bash
sudo ip           addr add 10.200.1.1/24 dev xdp-host
sudo ip -n xdp-ns addr add 10.200.1.2/24 dev xdp-peer
sudo ip -n xdp-ns addr add 10.200.1.3/24 dev xdp-peer
```

启用两端及 loopback：

```bash
sudo ip           link set xdp-host up
sudo ip -n xdp-ns link set xdp-peer up
sudo ip -n xdp-ns link set lo       up
```

## 挂载 XDP 过滤器

用 `BPF_LINK_CREATE` 把过滤器连接到网络接口。需要 BPF 程序的 fd 和接口索引；可用 `if_nametoindex` 从名称取得索引。

改进 `load_xdp.c`，使其接收接口名称，连接指定 XDP 过滤器，然后运行：

```bash
sudo ./load_xdp pass.bpf.bin xdp-host &
```

在已加载程序列表中找到过滤器：

```bash
sudo bpftool prog show
# 57: xdp  tag 57cd311f2e27366b  gpl
# 	loaded_at 2026-08-29T16:14:59+0000  uid 0
# 	xlated 16B  jited 23B  memlock 4096B
```

查看 xlated 指令：

```bash
sudo bpftool prog dump xlated tag 57cd311f2e27366b
#   0: (b7) r0 = 1
#   1: (95) exit
```

查看 JIT 编译代码：

```bash
sudo bpftool prog dump jited tag 57cd311f2e27366b
```

分析所见结果。

## 阻止 IPv4 数据帧

增加功能：读取 Ethernet 头，丢弃 IPv4 数据包。尝试：

```c
#include <linux/bpf.h>

struct eth {
  unsigned char dst[6];
  unsigned char src[6];
  unsigned short type;
} __attribute__((packed));

__attribute__((section("xdp"), used))
enum xdp_action bad(struct xdp_md *ctx) {
  void *data = (void *)(long)ctx->data;
  struct eth *eth = data;

  if (eth->type == __builtin_bswap16(0x0800)) {
    return XDP_DROP;
  }

  return XDP_PASS;
}
```

应得到 `Permission denied`。为什么？你能证明没有越过 `ctx` 指向的数据包缓冲区吗？[eBPF verifier](https://kernel-internals.org/bpf/bpf-verifier/) 也不能确认。

为读取验证器诊断，在 `BPF_PROG_LOAD` 中提供 `log_buf`：

```c
attr.log_buf = (__u64)log;
attr.log_size = sizeof(log);
attr.log_level = 1;
```

此时能看到解释：

```txt
0: R1=ctx() R10=fp0
0: (7b) *(u64 *)(r10 -16) = r1        ; R1=ctx() R10=fp0 fp-16_w=ctx()
1: (79) r1 = *(u64 *)(r10 -16)        ; R1_w=ctx() R10=fp0 fp-16_w=ctx()
2: (61) r1 = *(u32 *)(r1 +0)          ; R1_w=pkt(r=0)
3: (7b) *(u64 *)(r10 -24) = r1        ; R1_w=pkt(r=0) R10=fp0 fp-24_w=pkt(r=0)
4: (79) r1 = *(u64 *)(r10 -24)        ; R1_w=pkt(r=0) R10=fp0 fp-24_w=pkt(r=0)
5: (7b) *(u64 *)(r10 -32) = r1        ; R1_w=pkt(r=0) R10=fp0 fp-32_w=pkt(r=0)
6: (79) r1 = *(u64 *)(r10 -32)        ; R1_w=pkt(r=0) R10=fp0 fp-32_w=pkt(r=0)
7: (71) r2 = *(u8 *)(r1 +12)
invalid access to packet, off=12 size=1, R1(id=0,off=12,r=0)
R1 offset is outside of the packet
processed 8 insns (limit 1000000) max_states_per_insn 0 total_states 0 peak_states 0 mark_read 0
```

可以将诊断对应到原程序行，但这超出本教程范围。

修正程序，使 verifier 能证明它有效。再尝试构造不终止的过滤器，观察 verifier 的反应。

## 按 IP 过滤

实现阻止来源 IP `10.200.1.2` 数据包的 XDP 过滤器。

提示结构体：

```c
struct eth {
  __u8 dst[6];
  __u8 src[6];
  __u16 type;
} __attribute__((packed));

struct ipv4 {
  __u8 version_ihl;
  __u8 tos;
  __u16 length;
  __u16 id;
  __u16 fragment;
  __u8 ttl;
  __u8 protocol;
  __u16 checksum;
  __u32 src;
  __u32 dst;
} __attribute__((packed));
```

分别在开启和关闭过滤器时演示：

```bash
sudo ip netns exec xdp-ns ping -I 10.200.1.2 -c 3 10.200.1.1
sudo ip netns exec xdp-ns ping -I 10.200.1.3 -c 3 10.200.1.1
```

## 按 IP 限制 RPS

在 `rpc.bpf.c` 中实现更有用的过滤器：某 IP 的频率超过**每秒 5 个包**时，丢弃该 IP 的包。需要维护状态，并向用户空间报告每个 IP 的数据包处理统计。

内部状态及与用户空间通信的共享存储可通过 [BPF Maps](https://docs.ebpf.io/linux/concepts/maps/) 实现，可能写成全局变量。

研究新过滤器的字节码，注意 maps 访问处，应涉及宽的 `ldimm64` 指令。

从对象文件只提取字节码后，会有未解析的重定位。这样查看：

```bash
llvm-readelf -r rps.bpf.o
# Relocation section '.relxdp' at offset 0x710 contains 7 entries:
#     Offset             Info             Type               Symbol's Value  Symbol's Name
# 0000000000000188  0000001700000001 R_BPF_64_64            0000000000000000 .data
# 00000000000001a0  0000001900000001 R_BPF_64_64            0000000000000000 rates
# 00000000000001d0  0000001700000001 R_BPF_64_64            0000000000000000 .data
# 0000000000000240  0000001700000001 R_BPF_64_64            0000000000000000 .data
# 0000000000000258  0000001900000001 R_BPF_64_64            0000000000000000 rates
# 0000000000000378  0000001700000001 R_BPF_64_64            0000000000000000 .data
# 0000000000000390  0000001a00000001 R_BPF_64_64            0000000000000014 stats
```

重定位记录表示：指定 Offset 的指令中，对 Symbol Name 的引用尚未确定，需由 XDP 加载器解析。

新加载器先通过 `BPF_MAP_CREATE` 创建 maps，获得 fd；再修补未解析的 `ldimm64`，将 `src_reg` 设为 [BPF_PSEUDO_MAP_FD](https://github.com/torvalds/linux/blob/cf72cbb39da84b6f02f90c07f33b102fc10b16f0/include/uapi/linux/bpf.h#L1342-L1354)，`imm` 设为对应 fd。

允许通过 argv 传入偏移；自动化该过程是加分方向。

思考：

- `ldimm64` 还有哪些 `src_reg`？用途是什么？常见 BPF 工具如何处理？
- 非 BPF 编译过程如何解析重定位？静态库与动态库有什么区别？

还应实现读取 RPS 限速器统计信息的工具，可以整合进加载器。

使用以下命令验证：

```bash
sudo ip netns exec xdp-ns ping -I 10.200.1.2 -f -c 10000 10.200.1.1
sudo ip netns exec xdp-ns ping -I 10.200.1.3 -f -c 10000 10.200.1.1
```

## 迁移到 libbpf

用 `libbpf` 重写 RPS 限速器。

> 译者核对说明：原文先写 `rpc.bpf.c`，后面命令使用 `rps.bpf.o`，命名不一致；实现时自行统一。示例 `pass` 返回 `XDP_PASS`，但示例 xlated 输出写的是 `r0 = 1`，并非该返回值，不能当作应完全匹配的输出。当前目录仅提供 README，`pass.bpf.c`、`load_xdp.c` 等是学生需要创建的文件。
