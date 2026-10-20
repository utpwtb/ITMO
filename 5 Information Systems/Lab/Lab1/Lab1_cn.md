# 实验作业 № 1

变体编号：4101

注意！ 不同变体对应的作业内容不同！

## 1. 实验任务

实现一个信息系统，使用户能够对 `<span>Movie</span>` 类的对象进行操作。该类的定义如下：

```
public class Movie {
    private Long id;
    // 字段不能为 null
    // 字段值必须大于 0
    // 字段值必须唯一
    // 字段值必须自动生成

    private String name;
    // 字段不能为 null
    // 字符串不能为空

    private Coordinates coordinates;
    // 字段不能为 null

    private java.time.LocalDate creationDate;
    // 字段不能为 null
    // 字段值必须自动生成

    private int oscarsCount;
    // 字段值必须大于 0

    private long budget;
    // 字段值必须大于 0

    private Double totalBoxOffice;
    // 字段可以为 null
    // 字段值必须大于 0

    private MpaaRating mpaaRating;
    // 字段不能为 null

    private Person director;
    // 字段可以为 null

    private Person screenwriter;

    private Person operator;
    // 字段可以为 null

    private Integer length;
    // 字段不能为 null
    // 字段值必须大于 0

    private Long goldenPalmCount;
    // 字段值必须大于 0
    // 字段可以为 null

    private int usaBoxOffice;
    // 字段值必须大于 0

    private String tagline;
    // 字段不能为 null

    private MovieGenre genre;
    // 字段可以为 null
}

public class Coordinates {
    private Integer x;
    // 字段最大值为 826
    // 字段不能为 null

    private Integer y;
    // 字段不能为 null
}

public class Person {
    private String name;
    // 字段不能为 null
    // 字符串不能为空

    private Color eyeColor;
    // 字段可以为 null

    private Color hairColor;
    // 字段可以为 null

    private Location location;
    // 字段可以为 null

    private java.time.ZonedDateTime birthday;
    // 字段不能为 null

    private Float height;
    // 字段可以为 null
    // 字段值必须大于 0

    private Float weight;
    // 字段可以为 null
    // 字段值必须大于 0

    private String passportID;
    // 字段值必须唯一
    // 字段不能为 null
}

public class Location {
    private Long x;
    // 字段不能为 null

    private Double y;
    // 字段不能为 null

    private String name;
    // 字段不能为 null
}

public enum MpaaRating {
    G,
    PG,
    PG_13,
    R,
    NC_17;
}

public enum MovieGenre {
    WESTERN,
    COMEDY,
    TRAGEDY,
    HORROR;
}

public enum Color {
    GREEN,
    BLACK,
    ORANGE,
    WHITE,
    BROWN;
}

public enum Country {
    GERMANY,
    VATICAN,
    ITALY,
    NORTH_KOREA;
}
```

## 2. 系统要求

开发的信息系统必须满足以下要求：

1. 系统的主要用途

   信息系统的主要功能是管理根据指定变体中的类创建的对象。
2. 基本对象管理操作

   系统必须能够对对象执行以下操作：

   * 创建新对象。
   * 根据对象 ID 查询对象信息。
   * 更新对象（修改对象的属性）。
   * 删除对象。

   这些操作必须在应用程序中不同的窗口（界面）内完成。

   查询某个类的对象信息时，还必须同时显示与该对象相关联的其他对象的信息。
3. 对象关联功能

   创建类的对象时，必须允许用户将新对象与系统中已经存在的、可以与其关联的辅助类对象建立关联。
4. 服务器端处理

   对象管理操作必须在服务器端执行，而不是在客户端执行。

   所有修改都必须同步到数据库。
5. 主界面对象列表

   系统主界面必须以表格形式显示当前所有对象。

   * 对象的每个属性必须对应表格中的独立一列。
   * 如果对象数量过多，无法在一个屏幕中全部显示，则必须使用分页功能。
6. 筛选和排序

   必须支持根据任意字符串类型列的值，对表格中的对象进行筛选和排序。

   筛选必须采用完全匹配方式。

   例如，筛选 `<span>name </span><span>= </span><span>"Titanic"</span>` 时，只应匹配名称完全等于 `<span>Titanic</span>` 的对象，而不是名称中包含 `<span>Titanic</span>` 的所有对象。
7. 对象编辑入口

   用户必须能够通过以下位置进入对象更新（修改）界面：

   * 显示所有对象的主表格。
   * 对象可视化区域（如果实现了对象可视化功能）。
8. 多用户实时同步

   当一个用户添加、删除或修改对象时，其他已经登录系统的用户界面中，相应对象必须自动出现、消失或更新。
9. 关联对象删除

   如果删除某个对象时，该对象与其他对象存在关联，那么相关联的对象也必须被删除。
10. 查看权限、修改窗口与错误提示

    * 所有用户都必须能够查看所有对象。
    * 修改对象时，必须打开独立的对话框。
    * 如果用户在对象字段中输入了不正确的值，系统必须显示清晰、具有说明性的错误信息。

## 3. 特殊操作

系统必须提供一个独立的用户界面，用于对对象执行以下特殊操作：

1. 按美国票房删除电影

   删除所有 `<span>usaBoxOffice</span>` 字段值等于指定值的对象。
2. 计算平均美国票房

   计算所有对象的 `<span>usaBoxOffice</span>` 字段的平均值。
3. 按标语前缀查询电影

   返回一个对象数组，其中每个对象的 `<span>tagline</span>` 字段值都以指定的子字符串开头。
4. 重新分配奥斯卡奖项

   将某一种电影类型中的所有电影获得的奥斯卡奖项，均匀地重新分配给另一种电影类型中的电影。
5. 为指定时长以上的电影增加奥斯卡奖项

   对所有电影时长大于指定值的电影，额外授予指定数量的奥斯卡奖项。

重要要求：

上述特殊操作必须在应用程序的业务逻辑组件中实现，不能直接使用数据库的函数或存储过程来实现。

## 4. 对象存储的特殊要求

1. 关系型数据库

   必须使用关系型数据库管理系统 PostgreSQL 存储对象数据。

   信息系统所操作的每个对象都必须保存在数据库中。
2. 字段约束

   类中所有字段的要求（即类定义中注释所描述的约束），都必须同时在以下两个层面得到满足：

   * ORM（对象关系映射）层。
   * 数据库层。
3. ID 自动生成

   `<span>id</span>` 字段必须使用数据库提供的机制生成。
4. 数据库连接配置

   连接院系服务器上的数据库时，使用以下配置：

   | 配置项     | 值                       |
   | ---------- | ------------------------ |
   | 数据库主机 | `<span>pg</span>`      |
   | 数据库名称 | `<span>studs</span>`   |
   | 用户名     | 与登录服务器的用户名相同 |
   | 密码       | 与登录服务器的密码相同   |

## 5. 用户交互的组织要求

在开发系统时，必须考虑以下用户交互方面的要求：

1. 错误输入处理

   系统必须能够正确处理用户的不合法输入。

   具体包括：

   * 限制用户输入不允许的值。
   * 向用户说明输入错误的原因。
2. 菜单导航

   系统中不同的、逻辑上相互独立的功能模块之间，必须通过菜单进行切换。
3. 多客户端自动更新

   当某个用户添加、删除或修改对象时，该对象必须自动在其他所有客户端的相应显示区域中出现、消失或更新。

## 6. 开发技术要求

1. 基础技术

   必须使用 Java EE 和 Managed Beans（托管 Bean）作为实现信息系统的基础。
2. 持久化技术

   必须使用 EclipseLink 构建数据持久化层。
3. 分层架构

   应用程序的不同层必须彼此分离。

   信息系统中不同的逻辑功能部分必须放置在独立的组件中。

## 7. 实验报告内容

实验报告必须包含以下内容：

1. 实验任务的完整文本。
2. 所开发应用程序的 UML 类图和包图。
3. 系统源代码，或者包含系统源代码的代码仓库链接。
4. 实验总结与结论。

## 8. 实验答辩问题

1. 设计模式与架构模式。
2. Jakarta EE 平台及其组件类型。
3. Jakarta EE 中的托管 Bean（Managed Beans）和 CDI Bean。
4. ORM（对象关系映射）的概念。ORM 框架 Hibernate 和 EclipseLink 的特点、API、相似之处与区别。
5. Jakarta Persistence 技术的特点、API，以及它与 ORM 提供者的集成方式。
6. Jakarta Data 技术。
7. Spring 平台，以及 Spring 与 Java EE 的相似之处和区别。
8. Spring Boot。
9. Spring Data。
