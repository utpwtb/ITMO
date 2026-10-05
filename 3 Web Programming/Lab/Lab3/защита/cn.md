# 第三份实验报告的收获

## Hibernate会话接口

`org.hibernate.Session`接口是应用程序与Hibernate之间的桥梁。
所有与实体对象的CRUD操作都是通过会话来执行的。
`Session`类型的对象是从 `org.hibernate.SessionFactory`类型的实例中获取的，
该实例在应用程序中应以单例形式存在。
`session`的生命周期受限于逻辑事务的开始和结束。

### 实体对象的状态

- 瞬时对象（Transient object）—— 已填充的实体类实例。可以被保存到数据库。未附加到会话。`Id`字段不应被填充，否则对象将具有 `detached`状态。
- 持久化对象（Persistent object）—— 所谓的存储实体，它附加到特定的会话。只有在此状态下，对象才会与数据库交互。在事务中处理此类对象时，对象的所有更改都会写入数据库。
- 游离对象（Detached object）—— 与会话分离的对象，可能存在于数据库中，也可能不存在。

### Session接口中的一些方法

任何实体对象都可以从一种状态转换到另一种状态。为此，`Session`接口提供了以下方法：

- `persist(Object)` —— 将对象从_transient_状态转换为_persistent_状态，即附加到会话并保存到数据库。但是，如果我们为对象的 `Id`字段赋值，则会得到 `PersistentObjectException`，因为Hibernate会认为该对象是_detached_的，即存在于数据库中。保存时，_persist()_方法会立即执行_insert_，而不进行_select_。
- `merge(Object)` —— 将对象从_transient_或_detached_状态转换为persistent状态。如果是从_transient_状态转换，则其工作方式类似于_persist()_（为对象生成新的 `Id`，即使已设置），如果是从_detached_状态转换——则从数据库加载对象，附加到会话，并在保存时执行_update_查询。
- `replicate(Object, ReplicationMode)` —— 将对象从_detached_状态转换为_persistent_状态，同时对象必须事先设置好 `Id`。此方法旨在将具有指定 `Id`的对象保存到数据库，这是_persist()_和_merge()_方法不允许的。如果具有此 `Id`的对象已存在于数据库中，则行为根据枚举 `org.hibernate.ReplicationMode`中的规则确定：

  + `ReplicationMode.IGNORE` —— 数据库中的内容保持不变。
  + `ReplicationMode.OVERWRITE` —— 对象将保存到数据库，替换现有对象。
  + `ReplicationMode.LATEST_VERSION` —— 数据库中保存的是具有最新版本的对象。
  + `ReplicationMode.EXCEPTION` —— 生成异常。
- `delete(Object)` —— 从数据库中删除对象，换句话说，将_persistent_状态转换为_transient_状态。Object可以处于任何状态，主要条件是 `Id`必须已设置。
- `save(Object)` —— 将对象保存到数据库，生成新的 `Id`，即使已设置。Object可以处于_transient_或_detached_状态。
- `update(Object)` —— 更新数据库中的对象，将其转换为_persistent_状态（Object处于_detached_状态）。
- `saveOrUpdate(Object)` —— 调用_save()_或_update()_。
- `refresh(Object)` —— 通过向数据库执行_select_来更新_detached_对象，并将其转换为_persistent_状态。
- `get(Object.class, id)` —— 从数据库获取具有特定 `Id`的实体类对象，状态为_persistent_。

`Session`对象会缓存已加载的对象，从数据库加载对象时首先会检查缓存。为了从缓存中删除对象并将其与会话分离，使用 `session.evict(Object)`。`session.clear()`方法将对会话中的所有对象应用 `evict()`。

## EntityManager

是ORM的接口，用于管理持久化实体。

实体管理始于创建 `EntityManagerFactory`，它负责将对象映射到数据库、维护连接、状态缓存等等。

工厂创建 `EntityManager`对象，后者可以管理实体。`EntityManager`可以形成_persistence context_（持久化上下文）——从数据库加载或创建的实体实例集合（是在事务范围内的某种数据缓存）。EntityManager在事务提交时刻或显式调用flush()方法时，将所有在持久化上下文中的更改刷新到数据库。

- `persist()` —— 将新的托管实体实例引入持久化上下文。在事务提交时，通过SQL INSERT命令在数据库中创建相应的记录。
- `merge()` —— 将detached实体的状态转移到持久化上下文：从数据库加载具有相同id的实例，将传递的Detached实例的状态转移到其中，并返回加载的Managed实例。之后必须使用返回的Managed实例。
- `remove()` —— 从数据库中删除对象，或者，如果启用了软删除模式，则设置deleteTs和deletedBy属性。
- `find()` —— 按标识符加载实体实例。
- `fetch()` —— 确保为实体实例加载指定视图的所有属性，包括惰性（lazy）属性。实体实例必须处于Managed状态。
- `reload()` —— 用指定视图重新加载实体实例。确保加载视图的所有属性，内部调用fetch()方法。

# 来自se.ifmo的问题

## 1. JavaServer Faces技术。特点，与servlet和JSP的区别，优点和缺点。JSF应用程序的结构。

__JavaServer Faces (JSF)__ —— 是一个用于Web应用程序的框架，用于开发Java EE应用程序的用户界面。基于组件的使用。当用户请求新页面时，用户界面组件的状态会被保存，如果请求重复，则会恢复。

### JSF的优点

- 业务逻辑和界面的清晰分离
- 组件级别的管理
- 服务器端事件处理的简便性
- 可扩展性
- 不同开发商提供多种实现
- 集成开发工具（IDE）的广泛支持

### JSF的缺点

- 高级框架 —— 实现作者未预见的功能很复杂。
- 处理GET请求的困难（在JSF 2.0中已解决）。
- 开发自定义组件的复杂性。

### JSF应用程序的结构

- 包含GUI组件的JSP页面
- 标签库
- 托管Bean
- 附加对象（组件、转换器、验证器）
- 附加标签
- 配置 – faces-config.xml
- 部署描述符 – web.xml

## 2. 在JSF应用程序中使用JSP页面和Facelets模板。

JSF应用程序的界面由JSP（Java Server Pages）页面组成，这些页面包含提供界面功能的组件。同时，JSP标签库用于在JSF页面上渲染界面组件、注册事件处理器、将组件与数据验证器和转换器关联等等。

但并不能说JSF与JSP密不可分，因为JSP页面使用的标签只是通过名称访问组件来渲染它们。而JSF组件的生命周期并不局限于JSP页面。

## 3. JSF组件 - 实现特点，类层次结构。额外的组件库。JSF应用程序中的事件处理模型。

### JSF组件的实现特点

- 界面由组件构建。
- 组件位于JSP页面上。
- 组件实现 `javax.faces.component.UIComponent`接口。
- 可以创建自定义组件。
- 页面上的组件组合成树形结构——视图（view）。
- 视图的根元素是 `javax.faces.component.UIViewRoot`类的实例。

一些JSF组件：`<f:subview>`, `<h:selectOneMenu>`, `<h:selectOneRadio>`, `<h:selectOneListbox>`, `<h:selectManyCheckbox>`, ` <selectManyListbox>`, `<selectManyMenu>`, `<h:textArea>`, ...

```html
<h:selectOneListbox id="type" value="#{contactController.contact.type}">
<f:selectItem itemValue="PERSONAL" itemLabel="personal"/>
<f:selectItem itemValue="BUSINESS" itemLabel="business"/>
</h:selectOneListbox>
```

### 类层次结构（片段）

```
-- javax.faces.component.UIComponent
---- javax.faces.component.UIComponentBase
------ javax.faces.component.UIOutput
-------- javax.faces.component.UIInput
---------- javax.faces.component.UISelectOne
---------- javax.faces.component.UISelectMany
```

### 额外的组件库。

[PrimeFaces](https://www.primefaces.org/showcase/),
[RichFaces](http://docs.jboss.org/richfaces/latest_4_5_X/Developer_Guide/en-US/html/appe-Developer_Guide-Style_classes_and_skin_parameters.html),
[ICEFaces](http://www.icesoft.org/java/projects/ICEfaces/ace-components.jsf),
OpenFaces, Trinidad, Tomahawk.

### 事件处理模型

#### JSF应用程序中请求处理的生存周期由以下阶段组成：

1. 恢复视图
2. 应用请求参数；处理事件
3. 验证数据；处理事件
4. 更新模型数据；处理事件
5. 调用应用程序；处理事件

##### 渲染响应

1. __恢复视图阶段__：JSF运行时根据用户请求恢复视图：创建组件对象，分配事件监听器、转换器和验证器，所有视图元素放入FacesContext。
2. __应用请求值阶段__：将字符串值转换为组件所需类型。如果转换成功，则值保存在组件的本地变量中。如果失败，则创建错误消息并放入FacesContext。
3. __处理验证阶段__：调用为视图组件注册的验证器。如果组件值未通过验证，则创建错误消息并保存在FacesContext中。
4. __更新模型值阶段__：如果数据有效，则更新组件值。新值被分配给组件对象的字段。
5. __调用应用程序阶段__：控制权传递给事件监听器。形成新的组件值。
6. __渲染响应阶段__：根据请求处理结果更新视图。如果是第一次请求页面，则将组件放入视图层次结构中。生成服务器对请求的响应。在客户端，页面被更新。

## 4. 数据转换器和验证器。

JSF具有内置转换器并允许创建专门的转换器。

### **转换器 (Converter) 的作用**

 **转换器负责数据类型转换** ，在视图（字符串）和模型（对象）之间进行双向转换。

#### **主要职责：**

1. **格式化输出** ：对象 → 字符串（显示给用户）
2. **解析输入** ：字符串 → 对象（存储到后台）
3. **处理本地化** ：不同语言环境下的格式转换

### JSF标准转换器

- javax.faces.BigDecimal
- javax.faces.BigInteger
- javax.faces.Boolean
- javax.faces.Byte
- javax.faces.Character
- javax.faces.DateTime
- javax.faces.Double
- javax.faces.Float

```html
<h:outputLabel value="Age" for="age" accesskey="age" />
<h:inputText id="age" size="3" value="#{contactController.contact.age}">
</h:inputText>
```

```html
<h:outputLabel value="Birth Date" for="birthDate" accesskey="b" />
<h:inputText id="birthDate" value="#{contactController.contact.birthDate}">
<f:convertDateTime pattern="MM/yyyy"/>
</h:inputText>
```

### 专门的转换器

1. 创建实现Converter接口的类
2. 实现 `getAsObject()`方法，用于将字段的字符串值转换为对象。
3. 实现 `getAsString`方法。
4. 在faces-config.xml文件中使用 `<converter>`元素在Faces上下文中注册转换器。

__faces-config.xml文件__

```xml
<converter>
  <converter-for-class>
    com.arcmind.contact.model.Group
  </converter-for-class>
  <converter-class>
    com.arcmind.contact.converter.GroupConverter (com.arcmind.contact.converter.TagConverter)
  </converter-class>
</converter>
```

### 验证器

 **验证器负责数据验证** ，确保用户输入的数据符合业务规则。

#### **主要职责：**

1. **格式验证** ：检查数据格式是否正确
2. **范围验证** ：检查数值是否在允许范围内
3. **业务规则验证** ：检查是否符合特定业务逻辑
4. **必填验证** ：检查必填字段是否填写

#### 存在4种类型的验证器

1. 使用内置组件
2. 在应用程序级别
3. 使用服务器对象的验证方法（内联验证）
4. 使用实现Validator接口的专门组件

#### 1. 使用内置组件

1. DoubleRangeValidator
2. LongRangeValidator
3. LengthValidator

```html
<%-- 年龄 (age) --%>
<h:outputLabel value="Age" for="age" accesskey="age" />
<h:inputText id="age" size="3" value="#{contactController.contact.age}">
<f:validateLongRange minimum="0" maximum="150"/>
</h:inputText>
<h:message for="age" errorClass="errorClass" />
```

#### 2. 在应用程序级别

这直接就是业务逻辑。包括在托管bean对象的方法中添加代码，这些代码使用应用程序模型来验证已放入其中的数据。

#### 3. 使用服务器对象的验证方法

对于标准验证器不支持的数据类型，例如电子邮件地址，可以创建自己的验证组件。

#### 4. 使用实现Validator接口的专门组件

JSF允许创建可插拔的验证组件，这些组件可以在各种Web应用程序中使用。

这应该是一个实现Validator接口的类，其中实现了 `validate()`方法。需要在faces-config.xml文件中注册验证器。之后，可以在JSP页面上使用 `<f:validator/>`标签。

__faces-config.xml__

```xml
<validator>
  <validator-id>arcmind.zipCode</validator-id>
  <validator-class>com.arcmind.validators.ZipCodeValidator</validator-class>
</validator>
```

## 5. 服务器端JSF页面的表示。UIViewRoot类。

视图由以下部分负责：

`UI Component`。具有状态、方法、事件的对象，位于服务器上并负责与用户交互（可视化组件）。每个UI组件都包含一个 `render`方法，用于根据 `Render`类中的规则绘制自身。

`Renderer` - 负责组件的渲染和用户输入的转换。

`Validator`, `Convertor`

`Backing bean` - 从组件收集值，响应事件，与业务逻辑交互。

`Events`, `Listeners`, `Message`

`Navigation` - 页面间的导航规则，以XML文档形式定义。

### UIViewRoot

`UIViewRoot`对象表示JSF视图，它与活动的FacesContext相关联。JSF实现在首次访问（请求）时创建视图，或者恢复已创建的视图。当客户端提交表单（回发）时，JSF转换提交的数据，验证它们，保存到managed bean，为导航查找视图，从managed bean恢复组件值，根据视图生成响应。所有这些JSF操作都通过6个有序过程来描述。

`UIViewRoot` 是JSF框架的核心类，它代表了服务器端页面（视图）的完整结构。

### **主要特点：**

1. **视图的根组件** - 每个JSF页面对应一个UIViewRoot实例
2. **组件树的根** - 包含页面上所有UI组件的层级结构
3. **视图状态管理** - 负责保存和恢复视图状态
4. **生命周期管理** - 参与JSF请求处理生命周期

## 6. 托管Bean - 目的，配置方式。托管Bean的上下文。

__托管Bean__ – 包含用于处理组件数据的参数和方法的类。必须具有 `get`和 `set`方法。用于处理UI和验证数据。生命周期由JSF运行时环境管理。从JSP页面的访问通过表达式语言（EL）实现。配置在faces-config.xml中设置或通过注解完成。

### 托管Bean的配置

__faces-config.xml__

```xml
<managed-bean>
  <managed-bean-name>customer</managed-bean-name>
  <managed-bean-class>CustomerBean</managed-bean-class>
  <managed-bean-scope>request</managed-bean-scope>
  <managed-property>
    <property-name>areaCode</property-name>
    <value>#{initParam.defaultAreaCode}</value>
  </managed-property>
</managed-bean>
```

__使用注解__

```java
@ManagedBean(name="customer")
@RequestScoped
public class CustomerBean {
  @ManagedProperty(value="#{initParam.defaultAreaCode}" name="areaCode")
  private String areaCode;
  ...
}
```

`Managed bean` - 在JSF中注册的Bean，由JSF平台管理。Managed bean用作组件的模型，并具有自己的生命周期范围（scope），可以通过注解或在配置文件faces-config.xml中指定。

托管Bean具有__上下文__，它定义了其生命周期。它由注解指定。

### 注解

`@RequestScoped` - 默认使用。为每个HTTP请求（无论是发送还是接收）创建一个新的managed bean实例。_上下文 - 请求_

`@SessionScoped` - 实例在用户访问应用程序时创建一次，并在整个会话生命周期中使用。Managed bean必须是可序列化的。_上下文 — 会话_。

`@ApplicationScoped` - 实例在访问时创建一次，并在整个应用程序生命周期中使用。不应有状态，如果有，则必须同步访问，因为它对所有用户可用。_上下文 — 应用程序。_

`@ViewScoped` - 实例在访问页面时创建一次，并且只在使用者停留在页面上的时间内使用（包括ajax请求）。_上下文 — 页面，视图_。

`@CustomScoped(value="#{someMap}")` - 实例被创建并保存在Map中。程序员自己管理生命周期范围。

`@NoneScoped` - 创建实例，但不绑定到任何生命周期范围。当具有生命周期范围的其他managed bean引用它时使用。_无上下文的Bean。_

## 7. JSF应用程序的配置。faces-config.xml文件。FacesServlet类。

__faces-config.xml__ — JavaServer Faces的配置文件，必须位于项目的WEB-INF目录中。此文件可以包含managed bean的设置、转换器、验证器、本地化、导航以及其他与JSF相关的设置。

### faces-config.xml

```xml
<?xml version="1.0" encoding="UTF-8"?>
<faces-config xmlns="http://java.sun.com/xml/ns/javaee"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://java.sun.com/xml/ns/javaee
    http://java.sun.com/xml/ns/javaee/web-facesconfig_1_2.xsd"
    version="1.2">
  <managed-bean>
    <managed-bean-name>calculator</managed-bean-name>
    <managed-bean-class>com.arcmind.jsfquickstart.model.Calculator</managed-bean-class>
    <managed-bean-scope>request</managed-bean-scope>
  </managed-bean>
</faces-config>
```

托管对象的声明：对象的名称使用 `<managed-bean-name>`指定，类的全名 - `<managed-bean-class>`。托管对象的类必须包含无参构造函数。

`<managed-bean-scope>`定义JSF将在何处查找对象。如果对象绑定到视图并且在访问时不存在，则JSF将使用表达式语言EL API自动创建它。对象在处理一个请求期间可用。

默认使用faces-config，但可以在web.xml中列出额外的配置来使用它们。

### FacesServlet类

- 处理来自浏览器的请求。
- 形成事件对象并调用监听器方法。

**FacesServlet** 是JSF（JavaServer Faces）框架的 **前端控制器** ，负责处理所有JSF页面请求。

### **核心作用：**

1. **请求入口** ：拦截所有JSF请求（如：*.xhtml）
2. **生命周期管理** ：控制JSF的6个阶段处理流程
3. **上下文创建** ：为每个请求创建FacesContext环境

## 8. JSF应用程序中的导航。

JSF导航控制页面之间的跳转逻辑，决定用户操作后显示哪个页面。

JSF的导航机制允许定义逻辑结果标志与下一个视图之间的关联。由 `NavigationHandler`对象实现。导航通过转换规则完成。

可以通过三种不同的方式添加链接：

1. 使用commandLink和faces-config.xml中定义的普通转换规则

```xml
<navigation-rule>
  <navigation-case>
    <from-outcome>CALCULATOR</from-outcome>
    <to-view-id>/pages/calculator.jsp</to-view-id>
  </navigation-case>
</navigation-rule>
```

2. 使用commandLink和包含 `<redirect>`元素的转换规则。
3. 通过直接链接（`<h:outputLink>`元素）关联

```html
<h:outputLink value="pages/calculator.jsf">
<h:outputText value="Calculator Application (outputlink)"/>
</h:outputLink>
```

## 9. 从Java应用程序访问数据库。JDBC协议，查询形成，与数据库驱动程序的配合。

#### **1. JDBC (Java Database Connectivity)**

 **定义** ：Java数据库连接，是Java语言中用来规范客户端程序如何访问数据库的应用程序接口

 **关键特性** ：

* 提供与数据库无关的标准API
* 允许执行SQL语句
* 支持事务处理
* 提供数据库元数据访问

#### **2. JDBC驱动程序 (JDBC Driver)**

 **定义** ：实现JDBC接口的具体类库，用于连接特定数据库

### JDBC协议：

JDBC（Java Database Connectivity）不是协议，而是基于SQL访问组调用级别的接口。
JDBC本身不能工作，并使用ODBC的主要抽象和方法。尽管JDBC API标准规定了不仅可以通过ODBC工作，还可以通过使用两层或三层方案直接连接到数据库，但这种方案比普遍使用的 `JDBC-ODBC-Bridge`使用得少得多，后者在接口交互的总体方案中占据中心位置。

### 查询：

查询（query）——从数据库中选择必要信息的手段。使用两种类型的查询：按示例查询（QBE）和结构化查询语言（SQL）。有几种类型的查询：选择查询、更新查询、追加查询、删除查询、交叉表查询、创建表查询。选择查询用于选择用户需要的表中包含的信息，是最常用的。它们仅针对关联表创建。

### 数据库驱动程序：

有传递给查询的参数，最重要的是查询执行结果。驱动程序的任务是将查询、参数和结果打包成通过网络传输的数据包。打包格式在任何语言中都没有规定，每个DBMS都以自己的方式实现它。更何况，许多DBMS中不仅有不同的数据类型，还有复杂类型，例如PostgreSQL的数组，这在SQL标准中根本不存在，因此为了与DBMS配合工作，程序会与特定DBMS的库链接，这些库知道如何与特定的数据库通信。

// 1. 加载驱动程序
Class.forName("com.mysql.cj.jdbc.Driver");

// 2. 建立连接
Connection conn = DriverManager.getConnection(
    "jdbc:mysql://localhost:3306/mydb", "user", "password");

// 3. 创建语句
Statement stmt = conn.createStatement();

// 4. 执行查询
ResultSet rs = stmt.executeQuery("SELECT * FROM users");

// 5. 处理结果
while(rs.next()) {
    String name = rs.getString("name");
    int age = rs.getInt("age");
}

// 6. 关闭资源
rs.close();
stmt.close();
conn.close();

## 10. ORM概念。Java应用程序中的ORM库。主要API。ORM提供者与JDBC驱动程序的集成。

### ORM概念：

关系型DBMS – 以大家熟悉的表格形式存储数据，之所以应用如此广泛，完全是因为它们可靠、快速，而且最重要的是习惯。
面向对象的DBMS - 以程序员在代码中操作的完全相同的形式存储对象。
ORM使用特殊的框架或库，它们自己负责将程序中的对象与数据库表中的记录关联起来（我们使用ORM是因为我们使用java编写，而在那里操作的是对象，但我们需要与关系型DBMS交互）
Java中的ORM库：`ActiveJDBC`,`EclipseLink`,`Hibernate`,`Java Persistence API`

### 主要API：

Java Persistence API（JPA）——Java EE的API规范，提供了以方便的形式将Java对象保存到数据库的可能性，实现了ORM概念。这个接口有几种实现，最流行的一种使用Hibernate来实现。

## 11. ORM库Hibernate和EclipseLink。特点，API，异同。

### EclipseLink：

EclipseLink提供开源的JPA实现。此外，EclipseLink还支持许多其他持久性标准，例如Java Architecture for XML Binding（简单来说，JAXB不是将对象保存到数据库行中，而是将其映射到XML表示形式）。EclipseLink的主要优势之一是，您可以直接在JPQL查询中调用本机SQL函数。这在Hibernate中无法直接实现。EclipseLink提供了Hibernate中没有的其他选项。
例如：

- `@ReadOnly` - 指定实体仅用于读取
- `@Struct` - 定义一个类以映射到数据库结构类型。

### Hibernate：

但是Hibernate有更好的文档，以及更好的错误信息。例如，让我们看一下Hibernate提供的一些扩展 `@Entity`功能的注解：

- `@Table` - 允许指定为实体创建的表名
- `@BatchSize` - 指定从表中获取实体时的批处理大小
  还需要注意一些JPA中未规定的额外功能，这些功能在大型应用程序中可能很有用：
- 使用 `@SQLInsert`、`@SQLUpate`和 `@SQLDelete`注解的自定义CRUD语句
- 使用 `@Immutable`注解的不可变实体

还需要说，EclipseLink更符合标准，因为它是JPA 2的参考实现，Hibernate有一些兼容性问题，但它更成熟。

## 12. JPA技术。特点，API，与ORM提供者的集成。

JPA——这是一种技术，它提供了简单的JAVA对象的对象-关系映射，并提供了用于保存、获取和管理此类对象的API。
JPA本身既不能保存也不能管理对象，JPA只定义了规则：某些东西将如何工作。JPA还定义了提供者必须实现的接口。除此之外，JPA定义了应如何描述映射元数据以及提供者应如何工作的规则。然后，每个提供者实现JPA来定义对象的获取、保存和管理。每个提供者的实现都不同。

JPA提供的持久性支持涵盖以下领域：

- `javax.persistence`包中定义的API；
- 平台无关的面向对象的查询语言Java Persistence Query Language；
- 描述对象之间关系的元信息。
- 实体的DDL生成
