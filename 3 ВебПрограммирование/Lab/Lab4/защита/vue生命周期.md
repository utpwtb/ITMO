# 🇨🇳 Vue 组件生命周期详解

## 📋 生命周期图示

```
创建阶段：beforeCreate → created → beforeMount → mounted
更新阶段：beforeUpdate → updated
销毁阶段：beforeDestroy → destroyed (Vue 2) / beforeUnmount → unmounted (Vue 3)
激活阶段：activated → deactivated (keep-alive 缓存组件)
```

## 🔄 四个主要阶段

### 1. **创建阶段 (Creation)**

- **beforeCreate()**: 实例刚创建，数据观测和事件还未初始化
- **created()**: 实例创建完成，可以访问数据和方法，但 DOM 还未生成

### 2. **挂载阶段 (Mounting)**

- **beforeMount()**: 模板编译完成，但还未挂载到 DOM
- **mounted()**: 实例已挂载到 DOM，可以操作 DOM 元素

### 3. **更新阶段 (Updating)**

- **beforeUpdate()**: 数据变化时，DOM 更新之前
- **updated()**: 数据更新后，DOM 已重新渲染

### 4. **销毁阶段 (Destruction)**

- **beforeDestroy() / beforeUnmount()**: 实例销毁前
- **destroyed() / unmounted()**: 实例销毁后

## 🎯 常用钩子函数及用途

### **created()** - 最常用

```javascript
created() {
  // 1. 发起 API 请求
  this.fetchData()
  // 2. 初始化数据
  this.initData()
  // 3. 设置定时器
  this.timer = setInterval(...)
}
```

### **mounted()** - DOM 操作

```javascript
mounted() {
  // 1. 操作 DOM
  this.$refs.input.focus()
  // 2. 初始化第三方库
  this.initChart()
  // 3. 添加事件监听（非 Vue 事件）
  window.addEventListener('resize', this.handleResize)
}
```

### **beforeDestroy() / beforeUnmount()** - 清理资源

```javascript
beforeDestroy() {
  // 1. 清除定时器
  clearInterval(this.timer)
  // 2. 移除事件监听
  window.removeEventListener('resize', this.handleResize)
  // 3. 取消订阅
  this.unsubscribe()
}
```

## ⚠️ 注意事项

### **不要在 updated() 中修改数据**

```javascript
updated() {
  // ❌ 可能导致无限循环
  this.someData = newValue
  
  // ✅ 如果需要，使用条件判断
  if (this.needUpdate) {
    this.needUpdate = false
    this.doSomething()
  }
}
```

### **异步请求的时机**

```javascript
// ✅ 推荐：created 中发起请求
created() {
  this.loadData()
}

// ✅ 也可以：mounted 中发起
mounted() {
  // 如果需要 DOM 信息
  if (this.$refs.container) {
    this.loadData()
  }
}
```

## 🔧 Vue 2 vs Vue 3

| Vue 2         | Vue 3 (Options API) | Vue 3 (Composition API) |
| ------------- | ------------------- | ----------------------- |
| beforeCreate  | beforeCreate        | 在 setup() 开始时       |
| created       | created             | 在 setup() 中           |
| beforeMount   | beforeMount         | onBeforeMount()         |
| mounted       | mounted             | onMounted()             |
| beforeUpdate  | beforeUpdate        | onBeforeUpdate()        |
| updated       | updated             | onUpdated()             |
| beforeDestroy | beforeUnmount       | onBeforeUnmount()       |
| destroyed     | unmounted           | onUnmounted()           |

## 📊 父子组件生命周期顺序

### **加载时顺序**

```
父 beforeCreate → 父 created → 父 beforeMount → 
子 beforeCreate → 子 created → 子 beforeMount → 子 mounted → 
父 mounted
```

### **更新时顺序**

```
父 beforeUpdate → 子 beforeUpdate → 子 updated → 父 updated
```

### **销毁时顺序**

```
父 beforeDestroy → 子 beforeDestroy → 子 destroyed → 父 destroyed
```

---

# 🇷🇺 Жизненный цикл компонентов Vue

## 📋 Диаграмма жизненного цикла

```
Создание: beforeCreate → created → beforeMount → mounted
Обновление: beforeUpdate → updated
Уничтожение: beforeDestroy → destroyed (Vue 2) / beforeUnmount → unmounted (Vue 3)
Активация: activated → deactivated (кешированные компоненты keep-alive)
```

## 🔄 Четыре основные фазы

### 1. **Фаза создания (Создание)**

- **beforeCreate()**: Экземпляр только создан, данные и события еще не инициализированы
- **created()**: Экземпляр создан, доступны данные и методы, но DOM еще не сгенерирован

### 2. **Фаза монтирования (Монтирование)**

- **beforeMount()**: Шаблон скомпилирован, но еще не примонтирован к DOM
- **mounted()**: Экземпляр примонтирован к DOM, можно работать с DOM-элементами

### 3. **Фаза обновления (Обновление)**

- **beforeUpdate()**: Данные изменились, DOM еще не обновлен
- **updated()**: Данные обновлены, DOM перерендерился

### 4. **Фаза уничтожения (Уничтожение)**

- **beforeDestroy() / beforeUnmount()**: Перед уничтожением экземпляра
- **destroyed() / unmounted()**: После уничтожения экземпляра

## 🎯 Часто используемые хуки и их применение

### **created()** - самый часто используемый

```javascript
created() {
  // 1. Запросы к API
  this.fetchData()
  // 2. Инициализация данных
  this.initData()
  // 3. Установка таймеров
  this.timer = setInterval(...)
}
```

### **mounted()** - работа с DOM

```javascript
mounted() {
  // 1. Работа с DOM
  this.$refs.input.focus()
  // 2. Инициализация сторонних библиотек
  this.initChart()
  // 3. Добавление слушателей событий (не Vue-событий)
  window.addEventListener('resize', this.handleResize)
}
```

### **beforeDestroy() / beforeUnmount()** - очистка ресурсов

```javascript
beforeDestroy() {
  // 1. Очистка таймеров
  clearInterval(this.timer)
  // 2. Удаление слушателей событий
  window.removeEventListener('resize', this.handleResize)
  // 3. Отмена подписок
  this.unsubscribe()
}
```

## ⚠️ Важные замечания

### **Не изменяйте данные в updated()**

```javascript
updated() {
  // ❌ Может привести к бесконечному циклу
  this.someData = newValue
  
  // ✅ Если необходимо, используйте условную проверку
  if (this.needUpdate) {
    this.needUpdate = false
    this.doSomething()
  }
}
```

### **Время выполнения асинхронных запросов**

```javascript
// ✅ Рекомендуется: запросы в created
created() {
  this.loadData()
}

// ✅ Также можно: запросы в mounted
mounted() {
  // Если нужна информация о DOM
  if (this.$refs.container) {
    this.loadData()
  }
}
```

## 🔧 Vue 2 vs Vue 3

| Vue 2         | Vue 3 (Options API) | Vue 3 (Composition API) |
| ------------- | ------------------- | ----------------------- |
| beforeCreate  | beforeCreate        | В начале setup() |
| created       | created             | Внутри setup()    |
| beforeMount   | beforeMount         | onBeforeMount()         |
| mounted       | mounted             | onMounted()             |
| beforeUpdate  | beforeUpdate        | onBeforeUpdate()        |
| updated       | updated             | onUpdated()             |
| beforeDestroy | beforeUnmount       | onBeforeUnmount()       |
| destroyed     | unmounted           | onUnmounted()           |

## 📊 Порядок жизненного цикла родительских и дочерних компонентов

### **При загрузке**

```
Родитель beforeCreate → Родитель created → Родитель beforeMount → 
Дочерний beforeCreate → Дочерний created → Дочерний beforeMount → Дочерний mounted → 
Родитель mounted
```

### **При обновлении**

```
Родитель beforeUpdate → Дочерний beforeUpdate → Дочерний updated → Родитель updated
```

### **При уничтожении**

```
Родитель beforeDestroy → Дочерний beforeDestroy → Дочерний destroyed → Родитель destroyed
```

## 💡 Практические советы

1. **Используйте created** для инициализации данных и API-запросов
2. **Используйте mounted** для работы с DOM и сторонними библиотеками
3. **Всегда очищайте ресурсы** в beforeDestroy/beforeUnmount
4. **Будьте осторожны с updated** - избегайте изменения данных
5. **Помните о порядке выполнения** при работе с родительскими и дочерними компонентами
