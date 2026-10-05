# 实验提交与答辩流程

> 中文全译：[原文](https://github.com/secs-dev/os-course/blob/dee17bc418979ecbae3b45db74cdc1494bdc9bb1/doc/process.md)。

提交 `Xv6` 实验时，需要创建包含修改内容的 Pull Request（PR，拉取请求）。教师会在条件允许时审查代码；代码还必须通过测试运行器的检查。通过测试、解决教师提出的意见，并成功完成答辩（回答相关主题的问题）后，任务才算完成。

具体步骤如下。

## 第一步：创建仓库

使用课程仓库作为模板，创建一个私有仓库：

```text
Use this template -> Create Repository
```

设置仓库名称、描述和可见性：

- Repository name（仓库名称）：`os-course` / `xv6-riscv`。
- Description（描述）：`Repository for the ITMO CSE OS course. Student: P1111 Ivan Ivanov.`，按自己的班级和姓名修改。
- Choose visibility（可见性）：`Private`。

> [!WARNING]
> 仓库必须是 PRIVATE（私有），不能是 PUBLIC（公开）。

向实验课教师授予仓库的读取权限：

```text
Settings -> Collaborators and teams -> Add people
```

## 第二步：完成实验

1. 从 `main` 创建分支。分支名称必须是 `lab-<slug>`，其中 `slug` 是实验代号，例如 `lab-hugepage`。
2. 编写代码。
3. 如果任务尚未提供自动测试和 CI，则自行实现自动测试并配置 CI。
4. 创建从 `lab-<slug>` 合并到 `main` 的 PR。PR 描述要求见 [pull_request_template.md](https://github.com/secs-dev/os-course/blob/dee17bc418979ecbae3b45db74cdc1494bdc9bb1/.github/pull_request_template.md?plain=1)。
5. 通过自动检查。

说明：你可能不同意某些 lint 检查错误。明显不合理的规则可以禁用，但必须在 PR 评论中说明理由。

## 第三步：代码审查

1. 邀请实验课教师审查：在 PR 消息中用 `@somebody` **提及一次**教师。
2. 修正审查意见。
3. 获得教师认可，以及教师布置的附加任务。

## 第四步：实验答辩

1. 按照“附录 B”的要求编写[报告](report.md)。
2. 将报告发送到教师邮箱。邮件主题必须与 PR 标题一致。
3. 带着回答问题的准备来上课。
4. 完成答辩。
5. 获得成绩。

## 附录 B：报告的一般要求

详细报告编写规则见 [report.md](report.md)。

1. 文件名与 PR 标题一致。
2. 封面包含：机构、院系、实验名称（包括编号和标题）、学生完整姓名、班级、实验课教师完整姓名、年份。
3. 在“实验过程”一节开头放置链接。

## 附言

请保持 `main` 分支整洁 :D。避免无关修改，使 MR/PR 的 diff 易于阅读。若想作与实验无关的改动，例如重构构建系统、在内核中使用 `C++`，请先与教师协商。

> 译者注：第 3 条原文仅写“链接”，没有指定链接对象；结合前文的 PR 提交流程，通常可放本实验 PR 链接，但应以教师要求为准。
