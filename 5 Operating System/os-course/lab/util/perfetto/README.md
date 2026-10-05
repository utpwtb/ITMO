# Perfetto 使用说明

> 中文全译：[原文](https://github.com/secs-dev/os-course/blob/dee17bc418979ecbae3b45db74cdc1494bdc9bb1/lab/util/perfetto/README.md)。

下载 `tracebox`：

```sh
curl -LO get.perfetto.dev/tracebox
chmod +x ./tracebox
```

启动跟踪守护进程：

```sh
sudo ./tracebox traced
```

```sh
sudo ./tracebox traced_probes
```

执行跟踪：

```sh
sudo ./tracebox perfetto -c /mnt/utm-share/util/perfetto/config.txtpb --txt -o /tmp/trace.pftrace
# 将跟踪结果从内部存储复制到共享文件夹
sudo cp /tmp/trace.pftrace /mnt/utm-share/util/perfetto/
```

在浏览器打开 [Perfetto UI](https://ui.perfetto.dev/)，再把跟踪文件打开到网页应用中（支持拖放）。

通过 `WASD` 在跟踪视图中导航，参见 `SUPPORT > Keyboard Shortcuts`。

> 译者注：示例中的 `/mnt/utm-share/` 是原作者环境路径，使用时应换成自己的路径。[配置文件原文](https://github.com/secs-dev/os-course/blob/dee17bc418979ecbae3b45db74cdc1494bdc9bb1/lab/util/perfetto/config.txtpb)在远程仓库中。
