### **改进后的程序设计规范 (优化用户体验和健壮性)**

- [X] **1. 使用成熟的第三方库**

- **XML/JSON 解析** → 使用 `Jackson`、`Gson`（Java）或 `PyYAML`、`xml.etree`（Python），避免重复造轮子。
- **CSV → YAML**：如果默认是 CSV，改用 **YAML**（更易读，支持复杂结构）。

- [X] **2. 用户友好的提示**

- **启动时提示**：
  ```plaintext
  Type 'help' to see available commands.  
  Type 'exit' to quit.  
  ```
- **类似 Bash 的交互式提示**：
  ```plaintext
  user@program:~$ [command]  
  ```

  每条命令执行后，返回新的提示符。

- [ ] **3. 枚举 (Enum) 输入处理**

- **支持多种输入方式**（不区分大小写）：
  - `RED` / `red` → 枚举值
  - `1` → 按序号选择
- **错误输入时循环提示**，直到输入合法：
  ```plaintext
  Enter color (RED/GREEN/BLUE or 1/2/3):  
  Invalid input! Try again.  
  ```

- [X] **4. 数据输入校验**

- **明确提示数据类型和限制**：
  ```plaintext
  Enter age (integer, 0-120):  
  ```
- **错误时重新输入**，而不是直接终止命令。

- [ ] **5. 文件处理逻辑**

- **环境变量文件路径无效**：
  - 启动时加载空集合，**仅在 `save` 时报错**：
    ```plaintext
    Warning: File not found. Starting with empty collection.  
    Error on save: Cannot write to invalid path!  
    ```
- **文件不存在时自动创建**（`save`/`load`）。
- **无权限访问文件**：
  - 启动空集合并提示：
    ```plaintext
    Error: No read permission for file. Using empty collection.  
    ```
  - `save` 时拒绝操作并报错。

- [ ] **6. 递归脚本处理**

- **`execute_script` 必须支持嵌套脚本**，避免硬编码递归深度。
- **空行不报错**，静默跳过。
- **`add` 在脚本内运行时，继续从脚本读取输入**，而不是切回控制台。

- [ ] **7. 信号处理 (Ctrl+C / Ctrl+D)**

- **捕获中断信号**，安全保存数据（若文件可写）：
  ```plaintext
  ^C\nSaving data before exit... Done.  
  ```

- [ ] **8. 健壮的 `update` 命令**

- **先检查 ID 是否存在**，再请求新数据：

  ```plaintext
  Enter ID to update: 999  
  Error: ID 999 not found!  
  ```

  ```plaintext
  Enter ID to update: 123  
  Found item. Enter new values:  
  ```

- [ ] **9. 空集合友好提示**

- **所有查询类命令**（如 `show`, `filter`）在空集合时返回：
  ```plaintext
  The collection is empty. Use 'add' to insert data.  
  ```

---

### **示例交互流程**

```plaintext
> Type 'help' for commands.  
user@program:~$ add  
Enter name (string): Alice  
Enter color (RED/GREEN/BLUE or 1/2/3): green  
Added successfully!  

user@program:~$ update  
Enter ID: 123  
Found: Name="Alice", Color="GREEN"  
Enter new color (RED/GREEN/BLUE): 3  
Updated!  

user@program:~$ save  
Data saved to /path/data.yaml.  

user@program:~$ ^D  
Saving data... Done. Exiting.  
```

---

**目标**：减少用户挫败感，明确错误原因，避免意外终止，确保数据安全。
