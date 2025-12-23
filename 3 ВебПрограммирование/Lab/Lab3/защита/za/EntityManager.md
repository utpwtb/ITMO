# EntityManager详解与实体状态

## 一、EntityManager是什么？

### 1.1 基本定义

**EntityManager** 是JPA（Java Persistence API）的核心接口，负责管理实体对象的生命周期和与数据库的交互。它是应用程序与持久化上下文（Persistence Context）之间的桥梁。

```java
// EntityManager接口的主要方法
public interface EntityManager {
    // CRUD操作
    void persist(Object entity);      // 新增
    <T> T find(Class<T> entityClass, Object primaryKey); // 查询
    <T> T merge(T entity);            // 更新
    void remove(Object entity);       // 删除
  
    // 查询
    Query createQuery(String jpql);
    <T> TypedQuery<T> createQuery(CriteriaQuery<T> criteriaQuery);
  
    // 刷新和清除
    void flush();                     // 同步到数据库
    void clear();                     // 清除持久化上下文
  
    // 获取实体状态
    boolean contains(Object entity);  // 检查是否被管理
  
    // 其他
    void detach(Object entity);       // 分离实体
    void refresh(Object entity);      // 从数据库重新加载
    <T> T getReference(Class<T> entityClass, Object primaryKey);
}
```

### 1.2 EntityManager的获取方式

```java
// 方式1：通过EntityManagerFactory获取（标准方式）
EntityManagerFactory emf = Persistence.createEntityManagerFactory("my-pu");
EntityManager em = emf.createEntityManager();

// 方式2：在Java EE容器中通过@PersistenceContext注入
@Stateless
public class UserService {
    @PersistenceContext(unitName = "my-pu")
    private EntityManager em;  // 容器管理的EntityManager
  
    public void saveUser(User user) {
        em.persist(user);
    }
}

// 方式3：在Spring中通过@PersistenceContext注入
@Service
public class ProductService {
    @PersistenceContext
    private EntityManager em;
  
    @Transactional
    public Product save(Product product) {
        return em.merge(product);
    }
}
```

## 二、实体状态（Entity States）

### 2.1 四种实体状态

在JPA中，实体对象有四种明确的状态：

```
┌─────────────┐      persist()       ┌─────────────┐
│  瞬时状态   │ ───────────────────► │  托管状态   │
│ (New/       │                     │ (Managed/   │
│  Transient) │                     │  Persistent)│
└─────────────┘                     └─────────────┘
       │                                     │
       │ create with new()                   │ remove()
       │                                     │
       ▼                                     ▼
┌─────────────┐      merge()        ┌─────────────┐
│  游离状态   │ ◄─────────────────── │  删除状态   │
│ (Detached)  │                     │ (Removed)   │
└─────────────┘                     └─────────────┘
```

### 2.2 详细解释每种状态

#### **状态1：瞬时状态（Transient/New）**

- **特征**：
  - 刚刚用 `new`关键字创建的对象
  - 没有与任何EntityManager关联
  - 没有对应的数据库记录
  - ID字段为null（除非手动设置）

```java
// 示例：创建瞬时对象
User user = new User();
user.setName("张三");     // 瞬时状态
user.setEmail("zhang@example.com");

// 此时：
// - user对象不在任何持久化上下文中
// - 数据库中没有对应记录
// - em.contains(user) 返回 false
```

#### **状态2：托管状态（Managed/Persistent）**

- **特征**：
  - 对象与EntityManager关联
  - 在持久化上下文中被管理
  - 对对象的修改会被自动跟踪并同步到数据库

```java
// 将瞬时对象转为托管状态
EntityManager em = emf.createEntityManager();
em.getTransaction().begin();

User user = new User();
user.setName("张三");

em.persist(user);  // 转为托管状态！
// 现在：
// - em.contains(user) 返回 true
// - 对象在持久化上下文中
// - 修改会被自动同步

user.setName("李四");  // 自动生成UPDATE语句
em.getTransaction().commit();  // 执行INSERT
```

#### **状态3：游离状态（Detached）**

- **特征**：
  - 曾经是托管状态，但现在不再与EntityManager关联
  - 修改不会被自动同步到数据库
  - 需要重新关联才能更新

```java
User user = em.find(User.class, 1L);  // 托管状态
em.close();  // 关闭EntityManager

// 现在user是游离状态：
// - 不再被任何EntityManager管理
// - 修改不会自动同步
// - 但对象仍然持有数据

user.setName("王五");  // 修改不会立即同步到数据库

// 要同步修改，需要重新关联：
EntityManager em2 = emf.createEntityManager();
em2.getTransaction().begin();
User managedUser = em2.merge(user);  // 重新转为托管状态
em2.getTransaction().commit();  // 执行UPDATE
```

#### **状态4：删除状态（Removed）**

- **特征**：
  - 对象即将从数据库删除
  - 仍然在持久化上下文中，但标记为待删除
  - 事务提交时执行DELETE

```java
User user = em.find(User.class, 1L);  // 托管状态
em.remove(user);  // 转为删除状态

// 此时：
// - user仍在持久化上下文中
// - 标记为待删除
// - em.contains(user) 仍返回true

user.setName("改名也没用");  // 修改无效，仍会被删除

em.getTransaction().commit();  // 执行DELETE FROM users WHERE id=1
// 提交后，对象变回瞬时状态
```

## 三、EntityManager的核心方法详解

### 3.1 persist() - 持久化实体

```java
@Entity
public class Product {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;  // 创建时为null
    private String name;
    private BigDecimal price;
}

// 使用persist
EntityManager em = emf.createEntityManager();
em.getTransaction().begin();

Product product = new Product();  // 瞬时状态
product.setName("Laptop");
product.setPrice(new BigDecimal("999.99"));

em.persist(product);  // 转为托管状态
// 此时product.getId()可能仍为null（取决于ID生成策略）

em.getTransaction().commit();  // 执行INSERT，生成ID
// 提交后product.getId()有值了

em.close();
product.setPrice(new BigDecimal("899.99"));  // 游离状态，修改不自动同步
```

### 3.2 find() - 查找实体

```java
// 查找单个实体
User user = em.find(User.class, 1L);  // 立即执行SELECT查询
// 如果找到，返回托管状态对象
// 如果没找到，返回null

// 查找时的延迟行为
User user = em.getReference(User.class, 1L);  // 返回代理对象
// 不会立即查询数据库，只有访问非ID属性时才查询
System.out.println(user.getId());     // 不触发查询
System.out.println(user.getName());   // 触发SELECT查询
```

### 3.3 merge() - 合并实体

```java
// 场景：从HTTP请求接收的游离对象
User detachedUser = getUserFromRequest();  // 游离状态，有id=1

EntityManager em = emf.createEntityManager();
em.getTransaction().begin();

// merge的工作流程：
// 1. 检查持久化上下文是否有id=1的托管对象
// 2. 如果有，将detachedUser的值复制到托管对象
// 3. 如果没有，从数据库加载id=1的对象，再复制值
// 4. 返回托管状态的引用
User managedUser = em.merge(detachedUser);  // 游离 → 托管

// 重要：必须使用返回的对象！
managedUser.setName("New Name");  // ✅ 修改会被跟踪
// detachedUser.setName("xxx");    // ❌ 不会跟踪

em.getTransaction().commit();  // 执行UPDATE
```

### 3.4 remove() - 删除实体

```java
// 方式1：先查询再删除
User user = em.find(User.class, 1L);  // 必须是托管状态
em.remove(user);  // 标记为删除状态
em.flush();  // 执行DELETE

// 方式2：直接删除（需要知道ID）
User user = new User();
user.setId(1L);  // 设置ID
user = em.merge(user);  // 转为托管状态
em.remove(user);  // 然后删除

// 注意：删除后对象变回瞬时状态
em.remove(user);
System.out.println(user.getId());  // 仍有值，但对象已不被管理
```

### 3.5 flush() 和 clear() - 同步和清理

```java
// flush() - 将持久化上下文的变化同步到数据库
em.persist(user1);
em.persist(user2);
user1.setName("Updated");  // UPDATE

em.flush();  // 执行：INSERT user1, INSERT user2, UPDATE user1
// 但事务还未提交！

// clear() - 清除整个持久化上下文
em.clear();  // 所有托管对象变为游离状态

// 现在所有修改都丢失了，除非之前调用过flush()
```

## 四、持久化上下文（Persistence Context）

### 4.1 什么是持久化上下文？

持久化上下文是EntityManager内部的一个**缓存区域**，用于跟踪托管实体对象的状态变化。

```java
// 图解持久化上下文
┌─────────────────────────────────────────┐
│          EntityManager                  │
│  ┌───────────────────────────────────┐  │
│  │     持久化上下文 (一级缓存)         │  │
│  │  ┌─────┐  ┌─────┐  ┌─────┐       │  │
│  │  │用户1│  │产品A│  │订单X│  ...  │  │
│  │  └─────┘  └─────┘  └─────┘       │  │
│  │     托管状态对象                   │  │
│  └───────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

### 4.2 持久化上下文的特点

```java
EntityManager em1 = emf.createEntityManager();
EntityManager em2 = emf.createEntityManager();

// 特点1：每个EntityManager有自己的持久化上下文
User user1 = em1.find(User.class, 1L);  // 在em1的上下文中
User user2 = em2.find(User.class, 1L);  // 在em2的上下文中

user1.setName("Name1");
user2.setName("Name2");  // 两个上下文独立

// 特点2：同一上下文内保证对象唯一性
User a = em1.find(User.class, 1L);
User b = em1.find(User.class, 1L);
System.out.println(a == b);  // true！同一个对象引用

// 特点3：自动脏检查（Dirty Checking）
User user = em1.find(User.class, 1L);
user.setName("New Name");  // 修改属性

// 不需要调用update()！
em1.getTransaction().commit();  // 自动检测变化并生成UPDATE
```

## 五、实战示例：完整的状态转换

```java
@Entity
public class Book {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private String title;
    private String author;
    // getters/setters
}

public class BookService {
    @PersistenceContext
    private EntityManager em;
  
    @Transactional
    public void demoEntityStates() {
        // === 1. 瞬时状态 → 托管状态 ===
        Book book1 = new Book();
        book1.setTitle("Java编程思想");
        book1.setAuthor("Bruce Eckel");
        // 此时：瞬时状态
      
        em.persist(book1);  // 转为托管状态
        // 生成ID（如果使用自增）
        // 在持久化上下文中被跟踪
      
        // === 2. 修改托管对象 ===
        book1.setTitle("Java编程思想（第5版）");
        // 自动脏检查，事务提交时生成UPDATE
      
        // === 3. 查询返回托管对象 ===
        Book book2 = em.find(Book.class, 100L);
        // 如果找到：托管状态
        // 如果没找到：返回null
      
        // === 4. 游离状态示例 ===
        em.detach(book1);  // 显式分离
        // 或 em.clear(); 清除所有
        // 或 em.close(); 关闭EntityManager
      
        book1.setAuthor("New Author");  // 游离状态，修改不跟踪
      
        // === 5. 重新关联游离对象 ===
        Book managedBook = em.merge(book1);  // 重新托管
        // 事务提交时执行UPDATE
      
        // === 6. 删除状态 ===
        Book book3 = em.find(Book.class, 200L);
        em.remove(book3);  // 转为删除状态
        // 事务提交时执行DELETE
      
        // === 7. 状态检查 ===
        System.out.println("book1是否被管理: " + em.contains(book1));
        System.out.println("book3是否被管理: " + em.contains(book3));  // true，但标记为删除
    }
}
```

## 六、常见问题与陷阱

### 问题1：游离对象修改不生效

```java
// ❌ 错误方式
User user = em.find(User.class, 1L);
em.close();  // 变为游离状态
user.setName("New Name");  // 修改不会同步！

// ✅ 正确方式
User user = em.find(User.class, 1L);
user.setName("New Name");  // 托管状态下修改
// 或
User detached = ...;  // 游离对象
User managed = em.merge(detached);  // 重新托管
managed.setName("New Name");  // 使用返回的对象
```

### 问题2：persist()带有ID的对象

```java
User user = new User();
user.setId(100L);  // 手动设置ID
user.setName("Test");

// ❌ 可能抛出异常（取决于ID生成策略）
em.persist(user);  

// ✅ 使用merge()代替
em.merge(user);
```

### 问题3：事务边界问题

```java
// ❌ 事务外操作
User user = em.find(User.class, 1L);  // 无事务，可能延迟加载失败
System.out.println(user.getOrders());  // LazyInitializationException!

// ✅ 确保在事务内
@Transactional
public User getUserWithOrders(Long id) {
    User user = em.find(User.class, id);
    user.getOrders().size();  // 触发延迟加载，在事务内安全
    return user;
}
```

## 七、状态检测方法

```java
// 判断实体状态的方法
public EntityState getEntityState(EntityManager em, Object entity) {
    if (entity == null) {
        return EntityState.NULL;
    }
  
    // 检查是否在持久化上下文中
    if (em.contains(entity)) {
        // 检查是否标记为删除
        EntityEntry entry = getEntityEntry(em, entity);  // 需要Hibernate API
        if (entry != null && entry.getStatus() == Status.DELETED) {
            return EntityState.REMOVED;
        }
        return EntityState.MANAGED;
    }
  
    // 检查是否有ID（简单判断）
    Object id = getIdValue(entity);
    if (id == null) {
        return EntityState.TRANSIENT;
    }
  
    return EntityState.DETACHED;
}

// 实用工具方法
public static boolean isTransient(Object entity) {
    return getIdValue(entity) == null;
}

public static boolean isManaged(EntityManager em, Object entity) {
    return em.contains(entity);
}
```

## 总结

**EntityManager**：

- JPA操作的核心接口
- 管理实体生命周期和持久化上下文
- 提供CRUD和查询功能

**实体状态**：

1. **瞬时（Transient）**：刚创建，无ID，未关联
2. **托管（Managed）**：被EntityManager跟踪，自动同步
3. **游离（Detached）**：曾托管，现独立，需手动同步
4. **删除（Removed）**：标记为删除，事务提交时执行

理解这些概念是掌握JPA/Hibernate的关键！
