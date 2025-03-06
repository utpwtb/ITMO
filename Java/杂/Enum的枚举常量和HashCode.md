在Java中，枚举类（`enum`）的每个枚举值的哈希值由以下规则确定：

### **结论**
- **同一个枚举类中的不同枚举值，其哈希值一定不同**。  
- **不同枚举类中的枚举值，若其序数（`ordinal`）相同，哈希值可能相同，但它们的`equals()`方法会返回`false`**。

---

### **详细解释**
1. **枚举的哈希值实现**  
   Java中的枚举类继承自`java.lang.Enum`，而`Enum`类覆盖了`hashCode()`方法，**返回的是枚举常量的序数（`ordinal`）的哈希码**。  
   - `ordinal`是枚举值在声明时的位置（从0开始）。例如：
     ```java
     enum Color { RED, GREEN, BLUE } // RED.ordinal()=0，GREEN.ordinal()=1，BLUE.ordinal()=2
     ```
   - 哈希值为`ordinal`的哈希码，即直接返回`ordinal`值本身。例如：
     ```java
     System.out.println(Color.RED.hashCode());    // 输出 0
     System.out.println(Color.GREEN.hashCode());  // 输出 1
     ```

2. **同一枚举类中的不同枚举值**  
   - 因为每个枚举值的`ordinal`唯一，所以它们的哈希值必然不同。  
   - 示例：
     ```java
     enum Day { MON, TUE, WED } 
     // MON.hashCode()=0，TUE.hashCode()=1，WED.hashCode()=2
     ```

3. **不同枚举类中的枚举值**  
   - 若不同枚举类的枚举值序数相同，哈希值会相同，但它们属于不同类，通过`equals()`比较会返回`false`。  
   - 示例：
     ```java
     enum Size { SMALL, MEDIUM, LARGE } 
     // SMALL.ordinal()=0，哈希值为0

     enum Priority { LOW, MEDIUM, HIGH } 
     // LOW.ordinal()=0，哈希值也为0

     System.out.println(Size.SMALL.equals(Priority.LOW)); // false
     ```

---

### **验证代码**
```java
enum Color { RED, GREEN, BLUE }
enum Size { SMALL, MEDIUM, LARGE }

public class Main {
    public static void main(String[] args) {
        // 同一枚举类的不同枚举值
        System.out.println(Color.RED.hashCode());    // 0
        System.out.println(Color.GREEN.hashCode());  // 1

        // 不同枚举类的相同序数枚举值
        System.out.println(Size.SMALL.hashCode());   // 0（与Color.RED哈希值相同）
        System.out.println(Color.RED.equals(Size.SMALL)); // false
    }
}
```

---

### **关键点总结**
- **哈希值的唯一性**：同一枚举类中，不同枚举值的哈希值唯一。  
- **跨类的哈希冲突**：不同枚举类中，若序数相同，哈希值会相同，但通过`equals()`可区分。  
- **不可覆盖性**：`Enum`的`hashCode()`是`final`方法，无法被覆盖，确保行为一致。