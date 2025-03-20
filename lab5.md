实现一个控制台应用程序，该程序在交互模式下管理对象集合。集合中需要存储 `Person`类的对象，其描述如下。

开发的程序必须满足以下要求：

1. 程序管理的类实例集合必须实现默认排序。
2. 必须满足类字段的所有要求（以注释形式指定）。
3. 必须使用 `java.util.LinkedHashMap`类型的集合进行存储。
4. 启动应用程序时，集合应自动从文件中填充值。
5. 文件名应通过环境变量传递给程序。
6. 数据应以XML格式存储在文件中。
7. 必须使用 `java.io.FileReader`类实现从文件中读取数据。
8. 必须使用 `java.io.BufferedOutputStream`类实现将数据写入文件。
9. 程序中的所有类必须使用 `javadoc`格式进行文档化。
10. 程序必须能够正确处理错误数据（用户输入错误、文件访问权限不足等）。
11. 在交互模式下，程序必须支持执行以下命令：
    - √ `help`：显示可用命令的帮助信息。
    - √`info`：在标准输出流中显示集合的信息（类型、初始化日期、元素数量等）。
    - √`show`：在标准输出流中显示集合中所有元素的字符串表示形式。
    - √`insert null {element}`：添加具有指定键的新元素。
    - √`update id {element}`：更新集合中ID等于指定值的元素。
    - √`remove_key null`：根据键从集合中删除元素。
    - √`clear`：清空集合。
    - √`save`：将集合保存到文件中。
    - `execute_script file_name`：从指定文件中读取并执行脚本。脚本中包含的命令格式与用户在交互模式下输入的命令格式相同。
    - √`exit`：退出程序（不保存到文件）。
    - `remove_greater {element}`：从集合中删除所有大于指定元素的元素。
    - `remove_lower {element}`：从集合中删除所有小于指定元素的元素。
    - √`remove_greater_key null`：从集合中删除所有键大于指定值的元素。
    - √`min_by_creation_date`：输出集合中 `creationDate`字段值最小的任意对象。
    - √`filter_contains_name name`：输出 `name`字段值包含指定子字符串的元素。
    - √`filter_less_than_hair_color hairColor`：输出 `hairColor`字段值小于指定值的元素。

**命令输入格式：**

- 所有命令参数为标准数据类型（基本类型、包装类、`String`、日期类）时，应与命令名称在同一行输入。
- 所有复合数据类型（存储在集合中的类对象）应逐行输入每个字段。
- 输入复合数据类型时，应向用户显示包含字段名称的提示（例如，“请输入出生日期：”）。
- 如果字段是枚举类型，则应输入其常量之一的名称（同时应预先显示常量列表）。
- 如果用户输入不正确（输入的字符串不是枚举常量的名称、输入字符串而不是数字、输入的数字超出指定范围等），应显示错误消息并提示重新输入字段。
- 对于 `null`值，使用空字符串。
- 带有注释“此字段的值应自动生成”的字段不应由用户手动输入。

**CollectionManager中loadCollection方法**
**Person中updateNextId方法**

**集合中存储的类的描述：**

```java
public class Person {
    private long id; //字段值必须大于0，字段值必须唯一，此字段的值应自动生成
    private String name; //字段不能为null，字符串不能为空
    private Coordinates coordinates; //字段不能为null
    private java.util.Date creationDate; //字段不能为null，此字段的值应自动生成
    private long height; //字段值必须大于0
    private java.time.LocalDateTime birthday; //字段不能为null
    private Color eyeColor; //字段不能为null
    private Color hairColor; //字段不能为null
    private Location location; //字段不能为null
}

public class Coordinates {
    private float x;
    private long y; //字段的最大值：797
}

public class Location {
    private Double x; //字段不能为null
    private Integer y; //字段不能为null
    private Integer z; //字段不能为null
}

public enum Color {
    RED,
    BLACK,
    YELLOW,
    BROWN;
}

public enum Color {
    BLUE,
    YELLOW,
    WHITE,
    BROWN;
}
```



1. 切换到你想克隆仓库的目录（例如：Desktop/random_folder）  
2. 执行命令：  
   `git clone 仓库链接`  
3. 将你项目的所有类文件移动到 `src/main/java/itmo/programming` 目录中  
4. 解决因文件移动导致的导入冲突（import冲突）  
5. 在 `build.gradle.kts` 文件中声明所有依赖项（需要连接的库）  
6. 创建用于构建和运行项目的配置（用于测试构建和运行的完整性）  
7. 运行代码检查工具（linter），并根据提示修改代码中的错误  
8. 若所有错误已修复，提交更改：  
   ```bash
   git checkout -b new_branch
   git add .
   git commit -m "提交名称"
   git push
   ```  

以下是每一步的详细解释：

---

### **1. 切换到目标目录**  
**目的**：选择一个本地文件夹存放克隆的仓库。  
**操作方法**：  
- 打开终端（或命令行工具）。  
- 使用 `cd` 命令导航到目标路径。  
  ```bash
  cd Desktop/random_folder  # 示例：切换到桌面上的 random_folder 文件夹
  ```
**注意**：如果目录不存在，可用 `mkdir 文件夹名` 创建。

---

### **2. 克隆仓库**  
**目的**：将远程仓库的代码下载到本地。  
**操作方法**：  
- 复制仓库的 SSH 或 HTTPS 链接（如 `git@github.com:用户名/仓库名.git`）。  
- 执行克隆命令：  
  ```bash
  git clone 仓库链接  # 替换为实际链接
  ```
**常见问题**：  
- 若提示权限错误（如之前的公钥问题），需检查 [SSH 配置](https://docs.github.com/en/authentication/connecting-to-github-with-ssh) 或改用 HTTPS 链接。  
- 若仓库不存在或无权访问，需联系仓库管理员。

---

### **3. 移动项目文件**  
**目的**：将你的代码文件放入项目标准结构中。  
**操作方法**：  
- 手动或通过命令将 `.java` 等文件移动到 `src/main/java/itmo/programming` 目录。  
  ```bash
  mv /原路径/*.java /目标路径/src/main/java/itmo/programming/
  ```
**注意**：  
- `src/main/java` 是 Maven/Gradle 项目的标准源码目录，需符合此结构才能正常编译。  
- 确保文件的包声明（`package itmo.programming;`）与目录路径一致，否则会报错。

---

### **4. 解决导入冲突**  
**目的**：修复因文件路径变更导致的 `import` 错误。  
**常见场景**：  
- 其他文件通过 `import itmo.programming.类名;` 引用你的类，但路径不匹配。  
**解决方法**：  
- 检查所有 `import` 语句，确保路径与文件实际位置一致。  
- 若类名或包结构有变动，需同步修改所有引用处。

---

### **5. 配置依赖项**  
**目的**：声明项目所需的第三方库（如日志工具、数据库驱动等）。  
**操作方法**：  
- 打开 `build.gradle.kts` 文件。  
- 在 `dependencies { ... }` 块中添加需要的库，例如：  
  ```kotlin
  dependencies {
      implementation("org.apache.commons:commons-lang3:3.12.0") // 示例库
  }
  ```
**注意**：  
- 库的坐标（如 `group:name:version`）可在 [Maven Central](https://mvnrepository.com/) 查找。  
- 修改后需同步 Gradle（IDE 通常会自动提示）。

---

### **6. 创建运行配置**  
**目的**：设置一键编译和运行项目的快捷方式。  
**操作方法（以 IntelliJ 为例）**：  
1. 点击右上角 `Add Configuration` → `+` → `Application`。  
2. 填写配置名称，选择主类（包含 `main` 方法的类）。  
3. 指定 JVM 参数（如有需要）。  
**验证**：点击运行按钮，确保项目能正常启动且无编译错误。

---

### **7. 运行 Linter**  
**目的**：检查代码风格和潜在问题（如未使用的变量、格式错误）。  
**操作方法**：  
- 如果项目配置了 Checkstyle、PMD 等工具，直接在终端运行：  
  ```bash
  ./gradlew check  # Gradle 项目的常见命令
  ```
- IDE 通常内置代码检查功能（如 IntelliJ 的 `Analyze → Inspect Code`）。  
**修复建议**：根据提示逐条修改代码，例如调整缩进、删除冗余代码等。

---

### **8. 提交更改**  
**目的**：将修改推送到远程仓库的新分支。  
**分步操作**：  
1. **创建并切换到新分支**：  
   ```bash
   git checkout -b new_branch  # 分支名建议有描述性，如 "fix-login-bug"
   ```
2. **添加所有改动**：  
   ```bash
   git add .  # 添加当前目录下所有文件
   ```
3. **提交更改**：  
   ```bash
   git commit -m "修复导入冲突并添加依赖项"  # 提交信息需简明描述改动
   ```
4. **推送到远程**：  
   ```bash
   git push -u origin new_branch  # 首次推送需关联远程分支
   ```

---

