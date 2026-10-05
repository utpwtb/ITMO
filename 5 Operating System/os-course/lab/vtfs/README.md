# 实验：文件系统

> 中文全译：[原文](https://github.com/secs-dev/os-course/blob/dee17bc418979ecbae3b45db74cdc1494bdc9bb1/lab/vtfs/README.md)。示例代码保留原文逻辑，代码中的说明性注释译为中文。

Linux 是[宏内核][1]，即各部分在同一地址空间工作。但增加功能并不要求完整重编译内核：可以将新功能编写为内核模块，在运行期间按需加载、卸载。详见 William Stallings《操作系统：内部结构与设计原理》第 2.10 节。

模块可以实现自己的文件系统，用户使用时与 [ext4][2]、[NTFS][3] 类似。本任务实现简单文件系统，数据存在 RAM，或按需要存放远程服务器，但用户可像使用磁盘文件一样操作它。

原文建议使用独立虚拟机：内核代码错误可能使整个系统崩溃并丢失数据。应使用虚拟机，而非 Docker 这类容器。为什么？

## 辅助材料

- [The Linux Kernel Module Programming Guide][26]：Linux 内核模块开发参考。
- [A simple native file system for Linux kernel][27]：简单原生文件系统模块示例。
- [Linux Kernel Development，第 3 版][28]：第 13 章讲解 Linux 虚拟文件系统。
- [Understanding the Linux Kernel，第 3 版][29]：第 12 章讲解虚拟文件系统结构与工作方式。

## 第一部分：认识简单模块

先学习编译和加载基础模块。需要构建工具和**对应运行内核版本**的头文件：

```sh
sudo apt-get install build-essential linux-headers-`uname -r`
```

远程仓库的 [vtfs.c](https://github.com/secs-dev/os-course/blob/dee17bc418979ecbae3b45db74cdc1494bdc9bb1/lab/vtfs/source/vtfs.c) 与 [Makefile](https://github.com/secs-dev/os-course/blob/dee17bc418979ecbae3b45db74cdc1494bdc9bb1/lab/vtfs/Makefile) 已提供模块基础，请先阅读。

内核需要两个模块函数：初始化与清理，分别由 `module_init`、`module_exit` 指定。

与用户态代码的重要区别：内核代码没有标准 libc，例如不能使用其 `printf`。可通过 [printk][8] 输出到系统日志。

Makefile 指定 `vtfs` 模块由一个翻译单元 `vtfs` 组成。可以添加翻译单元，合理拆分代码。

编译模块：

```sh
make
```

模块构建与普通程序不同，Makefile 会通过内核构建环境处理，使用额外目标、变量以及其他隐含操作。

成功后，`source` 目录生成 `vtfs.ko`。加载时传入实际文件路径，带 `.ko` 扩展名：

```sh
sudo insmod source/vtfs.ko
```

消息不会显示在当前终端，而在系统日志中，用 `dmesg` 查看：

```sh
$ dmesg
<...>
[ 123.456789] [vtfs] VTFS joined the kernel
```

卸载用 `rmmod`，参数是模块名称，不带 `.ko`；可用 `lsmod` 检查：

```sh
$ sudo rmmod vtfs
$ dmesg
<...>
[ 123.987654] [vtfs] VTFS left the kernel
```

## 第二部分：准备文件系统

先让文件系统把数据存于 RAM，最初甚至只模拟文件存在，之后再扩展网络传输和远程存储。

操作系统提供：

- [register_filesystem][9]：注册新的文件系统驱动。
- [unregister_filesystem][10]：取消注册。

本阶段涉及：

- [inode][11]：文件元数据描述。原文列举名称、位置、类型（本实验为普通文件或目录）。
- [dentry][12]：原文将其概括为目录描述、内部 inode 列表、父目录信息等。
- [super_block][13]：整个文件系统的描述，包括根目录信息等。

注册和取消注册函数接收文件系统描述结构，先写成：

```c
struct file_system_type vtfs_fs_type = {
  .name = "vtfs",
  .mount = vtfs_mount,
  .kill_sb = vtfs_kill_sb,
};
```

这里加入两个用于挂载管理的字段。`mount` 是挂载时调用的函数指针，例如：

```c
struct dentry* vtfs_mount(
  struct file_system_type* fs_type,
  int flags,
  const char* token,
  void* data
) {
  struct dentry* ret = mount_nodev(fs_type, flags, data, vtfs_fill_super);
  if (ret == NULL) {
    printk(KERN_ERR "Can't mount file system");
  } else {
    printk(KERN_INFO "Mounted successfuly");
  }
  return ret;
}
```

每次用户挂载该文件系统，都会调用此函数。使用 [mount][14]：

```bash
sudo mount -t vtfs "<token>" "<path>"
```

`-t` 指定文件系统名称，对应 `name` 字段。还传入 token 和本地挂载目录，挂载目录应为空。

因为文件系统不位于物理块设备上，使用 [mount_nodev][15]：

```c
struct dentry* mount_nodev(
  struct file_system_type* fs_type,
  int flags, 
  void* data, 
  int (*fill_super)(struct super_block*, void*, int)
);
```

最后一个参数是 `fill_super` 函数指针，用于填写 `super_block`。可以先写成：

```c
int vtfs_fill_super(struct super_block *sb, void *data, int silent) {
  struct inode* inode = vtfs_get_inode(sb, NULL, S_IFDIR, 1000);

  sb->s_root = d_make_root(inode);
  if (sb->s_root == NULL) {
    return -ENOMEM;
  }

  printk(KERN_INFO "return 0\n");
  return 0;
}
```

这里不需要 `data` 和 `silent`。`vtfs_get_inode` 是尚需实现的函数，创建新 inode，此处用于根目录：

> 原文 TODO：需按较新 Linux 内核 API 更新 `inode_init_owner` 签名。

```c
struct inode* vtfs_get_inode(
  struct super_block* sb, 
  const struct inode* dir, 
  umode_t mode, 
  int i_ino
) {
  struct inode *inode = new_inode(sb);
  if (inode != NULL) {
    inode_init_owner(inode, dir, mode);
  }

  inode->i_ino = i_ino;
  return inode;
}
```

文件系统必须知道根目录在哪：把根 inode 传给 [d_make_root][16]，结果放到 `s_root`。本处将根目录编号设为 `1000`。

用 [new_inode][17] 创建 inode；再用 [inode_init_owner][18] 等设置属性，此处类型为目录。`umode_t` 是位掩码，取值见 [linux/stat.h][19]，同时描述对象类型和访问权限。

另一个字段 `kill_sb` 是卸载时调用的函数。原文在此阶段只输出日志：

```c
void vtfs_kill_sb(struct super_block* sb) {
  printk(KERN_INFO "vtfs super block is destroyed. Unmount successfully.\n");
}
```

不要忘记在模块初始化时注册文件系统，清理时取消注册。最后编译、加载、挂载：

```sh
sudo make
sudo insmod vtfs.ko
sudo mount -t vtfs "TODO" /mnt/vt
```

若实现正确，应无错误；但还不能进入 `/mnt/vt`，因为尚未实现文件系统导航。

卸载文件系统：

```sh
sudo umount /mnt/vt
```

## 第三部分：列出文件与目录

上一部分还无法进入目录：

```sh
$ sudo mount -t vtfs "TODO" /mnt/vt
$ cd /mnt/vt
-bash: cd: /mnt/vt: Not a directory
```

需要实现部分 inode 操作，并将 [inode_operations][20] 结构赋给节点的 `i_op`，例如：

```c
struct inode_operations vtfs_inode_ops = {
  .lookup = vtfs_lookup,
};
```

先实现 `lookup`，让操作系统查找、识别相应对象。签名：

```c
struct dentry* vtfs_lookup(
  struct inode* parent_inode,  // 父节点
  struct dentry* child_dentry, // 要访问的对象
  unsigned int flag            // 未使用的参数
);
```

暂时只返回 `NULL`。再次进入目录仍失败，但原因变为权限问题：

```sh
$ cd /mnt/vt
-bash: cd: /mnt/vt: Permission denied
```

解决权限问题。暂不需要复杂权限体系，所有对象可设权限 `777`，结果类似：

```sh
$ ls -l /mnt/
total 0
drwxrwxrwx 1 root root 0 Oct 24 15:52 vt
```

此时可以进入 `/mnt/vt`，但仍不能列出内容。需要把 [file_operations][21] 放入 `i_fop`，先实现 `iterate`。

> 原文 TODO：需按较新 Linux 内核 API 更新 `.iterate` 字段名。

```c
struct file_operations vtfs_dir_ops = {
  .iterate = vtfs_iterate,
};
```

它用于目录的非递归枚举：对每个对象调用 `dir_emit`，传入名称、inode 编号和类型。

原文给出的 `vtfs_iterate` 示例：

```c
int vtfs_iterate(struct file* filp, struct dir_context* ctx) {
  char fsname[10];
  struct dentry* dentry = filp->f_path.dentry;
  struct inode* inode   = dentry->d_inode;
  unsigned long offset  = filp->f_pos;
  int stored            = 0;
  ino_t ino             = inode->i_ino;

  unsigned char ftype;
  ino_t dino;
  while (true) {
    if (ino == 100) {
      if (offset == 0) {
        strcpy(fsname, ".");
        ftype = DT_DIR;
        dino = ino;
      } else if (offset == 1) {
        strcpy(fsname, "..");
        ftype = DT_DIR;
        dino = dentry->d_parent->d_inode->i_ino;
      } else if (offset == 2) {
        strcpy(fsname, "test.txt");
        ftype = DT_REG;
        dino = 101;
      } else {
        return stored;
      }
    }
  }
}
```

再次列目录：

```sh
$ ls /mnt/vt
ls: cannot access '/mnt/vt/test.txt': No such file or directory test.txt
```

错误原因是 `lookup` 还不能正确处理 `test.txt`；后续步骤修正。

## 第四部分：目录导航

扩展 `vtfs_lookup`：如果文件存在，调用 `d_add`，传入文件 inode。例如：

```c
struct dentry* vtfs_lookup(
  struct inode* parent_inode, 
  struct dentry* child_dentry, 
  unsigned int flag
) {
  ino_t root = parent_inode->i_ino;
  const char *name = child_dentry->d_name.name;
  if (root == 100 && !strcmp(name, "test.txt")) {
    struct inode *inode = vtfs_get_inode(parent_inode->i_sb, NULL, S_IFREG, 101);
    d_add(child_dentry, inode);
  } else if (root == 100 && !strcmp(name, "dir")) {
    struct inode *inode = vtfs_get_inode(parent_inode->i_sb, NULL, S_IFDIR, 200);
    d_add(child_dentry, inode);
  }
  return NULL;
}
```

## 第五部分：创建、删除文件

向 `inode_operations` 加入 `create` 和 `unlink`。创建文件时调用 `vtfs_create`；成功后通过 `d_add` 关联新 inode。简单示例：

> 原文 TODO：需按较新 Linux 内核 API 更新 `create` 函数签名。

```c
int vtfs_create(
  struct inode *parent_inode, 
  struct dentry *child_dentry, 
  umode_t mode, 
  bool b
) {
  ino_t root = parent_inode->i_ino;
  const char *name = child_dentry->d_name.name;
  if (root == 100 && !strcmp(name, "test.txt")) {
    struct inode *inode = vtfs_get_inode(
        parent_inode->i_sb, NULL, S_IFREG | S_IRWXUGO, 101);
    inode->i_op = &vtfs_inode_ops;
    inode->i_fop = NULL;

    d_add(child_dentry, inode);
    mask |= 1;
  } else if (root == 100 && !strcmp(name, "new_file.txt")) {
    struct inode *inode = vtfs_get_inode(
        parent_inode->i_sb, NULL, S_IFREG | S_IRWXUGO, 102);
    inode->i_op = &vtfs_inode_ops;
    inode->i_fop = NULL;

    d_add(child_dentry, inode);
    mask |= 2;
  }
  return 0;
}
```

用 `touch` 检查：

```sh
$ touch test.txt
$ ls
test.txt
$ touch new_file.txt
$ ls
test.txt new_file.txt
```

删除文件用 `vtfs_unlink`：

```c
int vtfs_unlink(struct inode *parent_inode, struct dentry *child_dentry) {
  const char *name = child_dentry->d_name.name;
  ino_t root = parent_inode->i_ino;
  if (root == 100 && !strcmp(name, "test.txt")) {
    mask &= ~1;
  } else if (root == 100 && !strcmp(name, "new_file.txt")) {
    mask &= ~2;
  }
  return 0;
}
```

此时能够使用 `rm`：

```sh
$ ls
test.txt new_file.txt
$ rm test.txt
$ ls
new_file.txt
$ rm new_file.txt
$ ls
```

注意 `touch` 会检查文件是否存在，因此会调用 `lookup`。

## 第六部分：实现 RAM 数据存储

此前只是文件系统桩代码，内容写死在源码里。现在应使用 RAM 存储数据，重新实现前面操作，例如使用数组和链表。

建议提前抽出文件系统接口，方便切换存储后端；后续阶段会用到。

## 第七部分：创建、删除目录

向 `inode_operations` 加入 `mkdir` 和 `rmdir`。函数签名见[内核定义][22]。

## 第八部分*：文件读写

实现文件读取和写入。普通文件也需要 `file_operations`，不只是目录；加入 [read][23] 与 [write][24]：

```c
ssize_t vtfs_read(
  struct file *filp, // 打开文件对象
  char *buffer,      // 用户空间读写缓冲区
  size_t len,        // 请求读写的数据长度
  loff_t *offset     // 偏移
);

ssize_t vtfs_write(
  struct file *filp, 
  const char *buffer, 
  size_t len, 
  loff_t *offset
);
```

不能直接访问用户空间的 `buffer`；使用专门的[用户态/内核态复制函数][25]。

完成后应能执行：

```sh
$ cat file1
hello world from file1
$ cat file2
file2 content here
$ echo "test" > file1
$ cat file1
test
```

文件必须能保存代码值为 0–127（含）的全部 ASCII 字符。

## 第九部分*：硬链接

支持从文件系统不同位置引用同一个 inode。

注意原文服务器只支持普通文件硬链接，不支持目录硬链接。

向 `inode_operations` 加入 `link`，签名：

```c
int vtfs_link(
  struct dentry *old_dentry, 
  struct inode *parent_dir, 
  struct dentry *new_dentry
);
```

完成后可执行：

```sh
$ ln file1 file3
$ cat file1
hello world from file1
$ cat file3
hello world from file1
$ echo "test" > file1
$ rm file1
$ cat file3
test
```

## 第十部分：文件系统服务器

当前文件系统数据不能在重启后保留。现在使用持久存储，并实现类似 `netfs` 的远程文件系统。

可以用任意编程语言实现服务器，可采用数据库存储，例如 Spring + PostgreSQL 或 ZIO + YDB。

内核网络 API 与常规用户态 API 不同，仓库提供自己的 HTTP 客户端：[http.c](https://github.com/secs-dev/os-course/blob/dee17bc418979ecbae3b45db74cdc1494bdc9bb1/lab/vtfs/source/http.c) 中的 `vtfs_http_call`：

```c
int64_t vtfs_http_call(
    const char *token,     // 访问令牌
    const char *method,    // 不带 fs 命名空间的方法名（list、create 等）
    char *response_buffer, // 保存服务器响应的缓冲区
    size_t buffer_size,    // 缓冲区大小
    size_t arg_size,       // 参数对数量
    // 随后传入 2 * arg_size 个 const char* 参数
    // - 请求参数对 param1、value1、param2、value2 等
    ... 
);
```

返回值：

- `0`：成功。
- 正数：服务器返回错误，含义见 API 文档。
- 负数：发起请求过程中的错误，例如无法连接、网络故障、无效响应，代码来自 [http.h](https://github.com/secs-dev/os-course/blob/dee17bc418979ecbae3b45db74cdc1494bdc9bb1/lab/vtfs/source/http.h) 或 `errno-base.h`（`ENOMEM`、`ENOSPC`）。

## 向教师提交的要求

- 报告包含仓库链接及工作结论。
- 准备按教师要求运行测试。

## 译者核对说明

以下是原文示例的现状说明，**不是新增任务，也不是已修复代码**：

- 前文根 inode 使用 `1000`，后续示例改成 `100`，实现时必须统一。
- `vtfs_iterate` 代码未给出完整的 `dir_emit`、偏移更新等步骤，直接照抄可能陷入循环。
- 原文已标出多处旧内核 API 的 TODO，应按实验使用的内核版本核对。
- 精确地说，文件名与名称查找主要通过 dentry 表示；inode 并不直接存放目录名称列表。上面的概述保留了原文语义。
- token 的取得方式、完整远程服务器 API 在当前 README 中没有给出。
- 星号仅按原文保留于第 8、9 部分；原文没有在此明确其是否必做，应由教师确定。

[1]: https://en.wikipedia.org/wiki/Monolithic_kernel
[2]: https://en.wikipedia.org/wiki/Ext4
[3]: https://en.wikipedia.org/wiki/NTFS
[5]: https://releases.ubuntu.com/22.04/
[8]: https://www.kernel.org/doc/html/latest/core-api/printk-basics.html
[9]: https://www.kernel.org/doc/htmldocs/filesystems/API-register-filesystem.html
[10]: https://www.kernel.org/doc/htmldocs/filesystems/API-unregister-filesystem.html
[11]: https://elixir.bootlin.com/linux/v5.15.53/source/include/linux/fs.h#L624
[12]: https://elixir.bootlin.com/linux/v5.15.53/source/include/linux/dcache.h#L91
[13]: https://elixir.bootlin.com/linux/v5.15.53/source/include/linux/fs.h#L146
[14]: https://linux.die.net/man/8/mount
[15]: https://elixir.bootlin.com/linux/v5.15.53/source/include/linux/fs.h#L2476
[16]: https://elixir.bootlin.com/linux/v5.15.53/source/fs/dcache.c#L2038
[17]: https://elixir.bootlin.com/linux/v5.15.53/source/fs/inode.c#L961
[18]: https://elixir.bootlin.com/linux/v5.15.53/source/fs/inode.c#L2159
[19]: https://elixir.bootlin.com/linux/v5.15.53/source/include/uapi/linux/stat.h#L9
[20]: https://elixir.bootlin.com/linux/v5.15.53/source/include/linux/fs.h#L2037
[21]: https://elixir.bootlin.com/linux/v5.15.53/source/include/linux/fs.h#L1995
[22]: https://elixir.bootlin.com/linux/v5.15.53/source/include/linux/fs.h#L2051
[23]: https://elixir.bootlin.com/linux/v5.15.53/source/include/linux/fs.h#L1998
[24]: https://elixir.bootlin.com/linux/v5.15.53/source/include/linux/fs.h#L1999
[25]: https://www.kernel.org/doc/htmldocs/kernel-hacking/routines-copy.html
[26]: https://sysprog21.github.io/lkmpg/
[27]: https://github.com/sysprog21/simplefs/
[28]: https://www.doc-developpement-durable.org/file/Projets-informatiques/cours-&-manuels-informatiques/Linux/Linux%20Kernel%20Development,%203rd%20Edition.pdf
[29]: https://www.amazon.com/Understanding-Linux-Kernel-Third-Daniel/dp/0596005652
