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
