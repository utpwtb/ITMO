# Gradle + Groovy 构建脚本实现报告

## 项目概览

本文档详细解释 `build.gradle` 中全部 16 个目标的实现原理、产生的文件及其存储位置。

### 核心文件

| 文件 | 作用 |
|------|------|
| `build.gradle` | 主构建脚本，包含全部任务逻辑 |
| `gradle.properties` | 变量/常量配置文件，所有参数集中管理 |
| `settings.gradle` | 项目名称定义 |
| `gradlew` / `gradlew.bat` | Gradle Wrapper，无需系统安装 Gradle |

---

## 脚本基础架构解释

### Groovy 是什么？

Groovy 是运行在 JVM 上的动态语言，语法兼容 Java 但更简洁。Gradle 使用 Groovy DSL（领域特定语言）来编写构建脚本。

### 脚本结构

```
build.gradle 的结构：
┌─────────────────────────────────────┐
│ plugins { }        ← 引入 Java/WAR 插件   │
│ repositories { }   ← 依赖下载地址         │
│ dependencies { }   ← 项目依赖库           │
│ war { }            ← WAR 包配置           │
│                                     │
│ task 任务名 { }     ← 16 个自定义任务      │
└─────────────────────────────────────┘
```

### 关键 Groovy 语法速查

```groovy
// 定义变量：def 关键字
def warFile = war.archiveFile.get().asFile

// 调用方法（括号可选）
file('build/libs')        // 等价于 file('build/libs')
copy { from 'a'; into 'b' }  // 闭包（closure），代码块作为参数传递

// 字符串插值
println "WAR: ${warFile.name}"  // ${} 内可写表达式

// .execute() 执行外部命令
['git', 'log'].execute()   // 执行 git log 命令

// dependsOn 声明任务依赖
task foo { dependsOn bar }  // foo 执行前必须先执行 bar
```

---

## 各任务详细实现

### 1. compile — 编译源代码

**命令**：`gradlew compile`

**实现原理**：
```groovy
task compile(group: 'build', description: '...') {
    dependsOn 'compileJava'    // ← 依赖 Gradle 内置编译任务
    doLast {
        println '[compile] 编译完成'
    }
}
```

- `compileJava` 是 Gradle `java` 插件提供的标准任务，自动编译 `src/main/java/` 下的所有 `.java` 文件
- `dependsOn` 表示：执行 compile 前，必须先执行完 compileJava
- `doLast` 是任务执行完后的回调（钩子函数）

**产生文件**：
- `build/classes/java/main/com/itmo/bean/*.class`
- `build/classes/java/main/com/itmo/model/dao/*.class`
- `build/classes/java/main/com/itmo/model/pojo/*.class`

---

### 2. build — 编译并打包为 WAR

**命令**：`gradlew buildProject`（用 buildProject 避免与系统 build 任务冲突）

**实现原理**：
```groovy
task buildProject(...) {
    dependsOn compile, war   // ← 先执行 compile，再执行 war
}
```

- `war` 是 Gradle `war` 插件提供的任务，将编译后的类 + webapp 文件打包成 `.war`
- MANIFEST.MF 自动包含：版本号、创建者、JDK 版本、操作系统信息

**关键配置**（来自 `war { manifest { ... } }` 块）：
```groovy
war {
    manifest {
        attributes(
            'Implementation-Version': project.version,  // 1.0-SNAPSHOT
            'Main-Class': 'com.itmo.bean.PointBean',
            ...
        )
    }
}
```

**产生文件**：
- `build/libs/WebLab3-1.0-SNAPSHOT.war` — 可直接部署到 WildFly 的 WAR 包

---

### 3. clean — 删除编译文件和临时目录

**命令**：`gradlew cleanAll`

**实现原理**：
```groovy
task cleanAll(...) {
    dependsOn clean  // ← Gradle 内置的 clean 任务（删除 build/ 目录）
    doLast {
        // 额外删除所有 **/temp/** 目录
        def tempDirs = fileTree(dir: projectDir, include: '**/temp/**')
        tempDirs.each { dir -> delete dir }
    }
}
```

- `fileTree(dir, include)` 搜索匹配模式的文件/目录树
- `each { }` 遍历集合，对每个元素执行闭包

---

### 4. test — 运行 JUnit 测试

**命令**：`gradlew runTests`

**实现原理**：
```groovy
task runTests(...) {
    dependsOn buildProject, test   // 必须先构建再测试
    test.mustRunAfter buildProject // 确保执行顺序
}
```

- 测试类：`src/test/java/com/itmo/PointBeanTest.java`
- 使用 JUnit 5（Jupiter），7 个测试用例：
  - 矩形区域命中测试（参数化，5 组数据）
  - 三角形区域命中测试（参数化，5 组数据）
  - 四分之一圆区域命中测试（参数化，5 组数据）
  - 边界外测试
  - 边界值测试
  - 空值参数测试

**为什么用反射测试私有方法**：
```java
Method method = PointBean.class.getDeclaredMethod("checkHit", double.class, double.class, double.class);
method.setAccessible(true);  // 绕过 private 限制
boolean result = (boolean) method.invoke(pointBean, x, y, r);
```
`checkHit()` 是 `private` 方法，无法直接调用。反射（reflection）可以在测试中访问私有方法。

**产生文件**：
- `build/reports/tests/test/index.html` — HTML 测试报告
- `build/test-results/test/*.xml` — XML 测试结果

---

### 5. xml — 验证 XML 文件

**命令**：`gradlew xmlValidate`

**实现原理**：
```groovy
task xmlValidate(...) {
    doLast {
        def xmlFiles = fileTree(dir: projectDir, include: '**/*.xml')
        xmlFiles.each { xmlFile ->
            def parser = new groovy.xml.XmlParser(false, false)
            parser.parse(xmlFile)  // 如果格式错误会抛异常
        }
    }
}
```

- `groovy.xml.XmlParser` 是 Groovy 内置的 XML 解析器
- `parse()` 方法会检查 XML 是否"格式良好"（well-formed）
- 遍历项目内所有 `.xml` 文件（12 个），逐一验证

**验证的文件**：
- `.idea/*.xml`（5 个 IDE 配置文件）
- `pom.xml`（Maven 配置）
- `src/main/resources/META-INF/persistence.xml`（JPA 配置）
- `src/main/webapp/WEB-INF/*.xml`（3 个 Java EE 配置）
- `org/hsqldb/main/module.xml`（HSQLDB 模块定义）

---

### 6. scp — SSH 传输 WAR 到远程服务器

**命令**：`gradlew scpDeploy`

**实现原理**：
```groovy
task scpDeploy(...) {
    dependsOn buildProject  // 先 build
    doLast {
        // 使用 Apache Ant 的 SCP 任务
        ant.taskdef(name: 'scp',
            classname: 'org.apache.tools.ant.taskdefs.optional.ssh.Scp',
            classpath: configurations.scpAntTask.asPath)
        ant.scp(
            file: warFile,                             // 要上传的文件
            todir: "${user}@${host}:${remotePath}",    // 目标地址
            port: port, password: password, trust: true
        )
    }
}
```

- 需要 `jsch`（Java SSH 库）和 `ant-jsch` 依赖
- 从 `gradle.properties` 读取：`scp.host`, `scp.port`, `scp.user`, `scp.password`, `scp.remote.deploy.path`
- WAR 上传到 `s407960@helios.cs.ifmo.ru:2222:/home/s407960/wildfly-21.0.0.Final/standalone/deployments/`

---

### 7. native2ascii — 本地化文件编码转换

**命令**：`gradlew native2ascii`

**实现原理**：
```groovy
task native2ascii(...) {
    doLast {
        propFiles.each { propFile ->
            ant.native2ascii(
                encoding: encoding,    // 目标编码 ISO-8859-1
                src: propFile.parentFile,
                dest: destDir,
                includes: propFile.name
            )
        }
    }
}
```

- `native2ascii` 是 JDK/Ant 自带的工具，将非 ASCII 字符（如俄语西里尔字母）转换为 `\uXXXX` Unicode 转义序列
- 例如 `Привет` → `\u041F\u0440\u0438\u0432\u0435\u0442`
- 这样可以在只支持 ASCII 的系统上安全存储和传输国际化文本

**源文件**：
- `src/main/resources/messages.properties`（英文，默认）
- `src/main/resources/messages_ru.properties`（俄语，含西里尔字符）

**产生文件**：
- `build/native2ascii/messages.properties` — ASCII 安全的副本
- `build/native2ascii/messages_ru.properties` — 西里尔字符转 `\uXXXX` 后的副本

---

### 8. music — 构建完成后播放音乐

**命令**：`gradlew music`

**实现原理**：
```groovy
task music(...) {
    dependsOn buildProject  // 先 build
    doLast {
        def audioStream = AudioSystem.getAudioInputStream(audioFile)
        def clip = AudioSystem.getClip()
        clip.open(audioStream)
        clip.start()
        // 等待播放完毕（最长 10 秒）
        def durationMs = (long) (clip.getMicrosecondLength() / 1000)
        Thread.sleep(Math.min(durationMs, 10000L))
        clip.close()
    }
}
```

- 使用 Java 标准库 `javax.sound.sampled` API
- `AudioSystem.getAudioInputStream()` 读取 WAV 文件
- `Clip` 是音频播放器，`start()` 开始播放
- `Thread.sleep()` 等待播放完成

**所需文件**：
- `lib/` 目录下的 `.wav` 文件（路径在 `gradle.properties` 的 `music.file` 配置）

---

### 9. doc — 生成摘要和 Javadoc

**命令**：`gradlew doc`

**实现原理**：
```groovy
task doc(...) {
    dependsOn buildProject, javadoc   // ← javadoc 是 Gradle 内置任务
    doLast {
        // 计算 WAR 文件的 MD5 和 SHA-1 摘要
        def md5  = computeDigest(warFile, 'MD5')
        def sha1 = computeDigest(warFile, 'SHA-1')
        // 写入 MANIFEST.MF
        manifestFile << "WAR-MD5: ${md5}\n"
        manifestFile << "WAR-SHA1: ${sha1}\n"
    }
}
```

**MD5/SHA-1 摘要计算函数**：
```groovy
def computeDigest(File file, String algorithm) {
    def digest = MessageDigest.getInstance(algorithm)  // 获取摘要算法
    file.eachByte(4096) { buf, len -> digest.update(buf, 0, len) }  // 分块读取
    return digest.digest().encodeHex().toString()  // 转十六进制字符串
}
```
逐块读取文件避免大文件撑爆内存。

**产生文件**：
- `build/tmp/doc/MANIFEST.MF` — 含 MD5、SHA-1 摘要的清单文件
- `build/docs/javadoc/` — 所有类的 API 文档（HTML）

---

### 10. history — 编译失败时 Git 历史回溯

**命令**：`gradlew history`

**实现原理**：
```groovy
task history(...) {
    doLast {
        // 1. 尝试编译当前源码
        def ok = tryCompile()
        if (ok) return  // 当前版本能编译，不需要回退

        // 2. 获取所有 Git 提交的 hash
        def commits = ['git', 'log', '--format=%H'].execute().text.readLines()

        // 3. 逐个 checkout 历史版本，尝试编译
        for (int i = 1; i < commits.size(); i++) {
            def hash = commits[i]
            ['git', 'archive', hash].execute()   // 导出该版本源码
            // 复制 build.gradle 到历史目录
            // 运行 gradlew compile
            if (编译成功) { workingCommit = hash; break }
        }

        // 4. 对第一个失败的提交生成 diff
        ['git', 'diff', "${workingCommit}..${brokenCommit}"].execute()
    }
}
```

**核心逻辑**：
1. 用 `tryCompile()` 测试当前能否编译（删除旧 .class 后重新编译）
2. 用 `git log --format=%H` 获取所有提交哈希
3. 用 `git archive <hash>` 导出旧版本源码（不改变工作区）
4. 在临时目录中复制 build.gradle 并运行 `gradlew compile`
5. 找到第一个能编译的版本后，用 `git diff A..B` 生成补丁文件

**产生文件**（仅在编译失败且找到可工作版本时）：
- `build/history/diffs/diff_<旧版>_to_<新版>.patch`

---

### 11. team — 构建前两个 Git 版本并打包

**命令**：`gradlew team`

**实现原理**：
```groovy
task team(...) {
    doLast {
        // 1. 获取最近 3 个提交
        def commits = ['git', 'log', '--format=%H', '-n', '3'].execute().text.readLines()
        // 2. 取前两个（跳过 HEAD）
        def prevRevs = [commits[1], commits[2]]
        // 3. 逐个导出、复制构建脚本、运行 gradlew war
        prevRevs.each { hash ->
            ['git', 'archive', hash].execute()  // 导出源码
            // 复制 build.gradle, gradlew 等到导出目录
            // 在导出目录中运行 gradlew war
        }
        // 4. 将所有 WAR 打包成 ZIP
        ant.zip(destfile: zipFile) { fileset(dir: archiveDir, includes: '*.war') }
    }
}
```

**产生文件**：
- `build/team/output/WebLab3_rev1_<hash>.war`
- `build/team/output/WebLab3_rev2_<hash>.war`
- `build/team/team_previous_versions.zip` — 以上两个 WAR 的 ZIP 包

---

### 12. alt — 创建类名/变量名替换后的替代版本

**命令**：`gradlew alt`

**实现原理**：
```groovy
task alt(...) {
    doLast {
        // 1. 复制源码到临时目录
        copy { from 'src/main/java'; into altSrcDir }

        // 2. 读取 gradle.properties 中的替换规则
        //    例如：alt.replace.class.PointBean=PointBeanAlt
        //          alt.replace.variable.x=xCoord

        // 3. 对每个 Java 文件执行文本替换
        javaFiles.each { javaFile ->
            replacements.each { oldName, newName ->
                content = content.replaceAll(~/\b${oldName}\b/, newName)
            }
        }

        // 4. 重命名文件（Java 要求文件名=类名）
        //    PointBean.java → PointBeanAlt.java

        // 5. 在替代目录中运行 gradlew war 构建
        pb.directory(altDir)
        pb.command('cmd', '/c', 'gradlew.bat war').start()
        // 6. 将构建结果复制回主 build/libs/
    }
}
```

**替换规则**（来自 `gradle.properties`）：

| 类型 | 原名 | 新名 |
|------|------|------|
| 类名 | PointBean | PointBeanAlt |
| 类名 | ResultsBean | ResultsBeanAlt |
| 类名 | Point | PointAlt |
| 类名 | PointDao | PointDaoAlt |
| 变量 | submitSource | submitType |

**正则表达式**：`~\bPointBean\b` 中的 `\b` 是单词边界，确保 `PointBean` 只匹配完整的类名，不会误匹配 `PointBeanTest` 之类的。

**产生文件**：
- `build/libs/WebLab3_alt-1.0-SNAPSHOT.war` — 替代版本 WAR

---

### 13. report — 测试报告提交到 Git

**命令**：`gradlew report`

**实现原理**：
```groovy
task report(...) {
    dependsOn runTests  // 先运行测试（runTests 依赖 buildProject 依赖 compile）
    doLast {
        // 1. 复制 JUnit XML 报告到专用目录
        copy { from xmlReportDir; into destDir }
        // 2. 用 git add + git commit 提交
        ['git', 'add', destDir].execute()
        ['git', 'commit', '-m', 'JUnit test report'].execute()
    }
}
```

**产生文件**：
- `build/reports/junit-xml/TEST-com.itmo.PointBeanTest.xml` — JUnit XML 格式报告

---

### 14. env — 替代 Java 环境构建

**命令**：`gradlew env`

**实现原理**：
```groovy
task env(...) {
    doLast {
        // 1. 读取 gradle.properties 中的替代 Java 路径和 JVM 参数
        def altJavaHome = props['alt.java.home']
        def jvmArgs = props['alt.jvm.args']

        // 2. 通过 ProcessBuilder 设置环境变量
        pb.environment().put('JAVA_HOME', altJavaHome)
        pb.environment().put('GRADLE_OPTS', jvmArgs)

        // 3. 在当前项目目录运行 gradlew war
        pb.command('cmd', '/c', 'gradlew.bat', 'war').start()
    }
}
```

**`gradle.properties` 中的配置**：
```properties
alt.java.home=C:/Program Files/Java/jdk-21   # 替代 JDK 路径
alt.jvm.args=-Xmx512m -Dfile.encoding=UTF-8  # JVM 内存和编码参数
```

**用途**：验证项目在另一版本的 JDK（如 JDK 17 vs 21）或不同 JVM 参数下能否正常构建。

---

### 15. diff — 条件 Git 提交

**命令**：`gradlew diff`

**实现原理**：
```groovy
task diff(...) {
    doLast {
        // 1. 检查 Git 工作区状态
        def changedFiles = ['git', 'status', '--porcelain'].execute().text

        // 2. 检查排除类是否被修改
        excludedClasses.each { className ->
            if (changedFiles.contains(className + '.java')) {
                excludedChanged = true  // 排除类被改了，不提交
            }
        }

        // 3. 只有排除类未被修改时才提交
        if (!excludedChanged) {
            ['git', 'add', '.'].execute()
            ['git', 'commit', '-m', 'Auto-commit: safe changes'].execute()
        }
    }
}
```

**排除规则**：在 `gradle.properties` 的 `diff.excluded.classes=PointBean` 中指定——如果 `PointBean.java` 被修改了，就不执行自动提交。

---

### 16. 未单独列出的目标

| 目标 | 类型 | 实现方式 |
|------|------|----------|
| processResources | 内置 | 复制 `src/main/resources/` 到 `build/resources/` |
| classes | 内置 | 编译 + 资源处理 |
| testClasses | 内置 | 编译测试源码 |

---

## 构建产物总览

```
WebLab3/
└── build/
    ├── classes/java/main/        ← compile 产物
    │   └── com/itmo/...
    ├── libs/
    │   ├── WebLab3-1.0-SNAPSHOT.war       ← build 产物
    │   └── WebLab3_alt-1.0-SNAPSHOT.war   ← alt 产物
    ├── docs/javadoc/             ← doc 产物（Javadoc HTML）
    ├── tmp/doc/MANIFEST.MF       ← doc 产物（含 MD5/SHA-1）
    ├── native2ascii/             ← native2ascii 产物
    ├── reports/
    │   ├── tests/test/           ← test 产物（HTML 报告）
    │   └── junit-xml/            ← report 产物（XML 报告）
    ├── team/
    │   ├── output/*.war          ← team 产物（历史版本 WAR）
    │   └── team_previous_versions.zip  ← team 产物
    ├── history/diffs/            ← history 产物（diff 补丁）
    └── alt-*/                    ← alt 工作目录（时间戳命名）
```

## 快捷命令参考

| 命令 | 作用 |
|------|------|
| `./gradlew tasks --group=build` | 列出所有 build 组任务 |
| `./gradlew tasks --group=verification` | 列出所有验证组任务 |
| `./gradlew <任务名> --info` | 详细日志模式运行 |
| `./gradlew <任务名> --scan` | 生成构建扫描报告 |
| `./gradlew --stop` | 停止所有 Gradle 守护进程 |
