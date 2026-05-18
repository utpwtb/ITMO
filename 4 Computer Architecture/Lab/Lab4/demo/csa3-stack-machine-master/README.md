# Лабораторная №3. Эксперимент.

- Барсуков Максим Андреевич, P3215
- Вариант: `alg -> asm | stack | harv | hw | tick -> instr | struct | stream | port | pstr | prob2 | cache`
- **Упрощённый вариант**: `asm | stack | harv | hw | instr | struct | stream | port | pstr | prob2`

## Язык программирования
### Синтаксис

Расширенная форма Бэкуса —Наура:

``` ebnf
<program> ::= <section_data> <section_text> | <section_text> <section_data> | <section_text>

<section_data> ::= ".data\n" <declaration>*
<section_text> ::= ".text\n" (<label_def> | <instruction> | <label_def> <instruction>)*

<declaration> ::= <label_def> (<array> | <reserve>)
<instruction> ::= <label_arg_command> | <number_arg_command> | <without_arg_command>

<label_def> ::= (<name> ":" (" ")*) | (<name> ":" (" ")* "\n")

<array> ::= (<array_element> "," (" ")*)* <array_element>+
<reserve> ::= "res" (" ")+ <number>
<array_element> ::= ("\"" <any_ascii> "\"" | <number>)

<label_arg_command> ::= ("push" | "jump" | "jz" | "jnz" | "js" | "jns" | "call") (" ")+ <name>

<number_arg_command> ::= ("push" | "input" | "output") (" ")+ <number>

<without_arg_command> ::= ("nop" | "halt" | "add" | "sub" | "mul" | "div" | "mod"
| "cmp" | "and" | "or" | "xor" | "inc" | "dec" | "neg" | "not" | "ret" | "pop"
| "swap" | "dup" | "over" | "over3" | "load" | "store" | "debug")

<number> ::= [-2^31; 2^31 - 1]
<name> ::= (<letter_or_>)+
<letter_or_> ::= <letter> | ("_")
<letter> ::= [a-z] | [A-Z]
``` 

### Семантика

- `.text` -- секция, в которой все последующие слова (до конца файла или объявления `.data`) интерпретируются, как инструкции или их аргументы или комментарии или метки;
- `.data` -- секция, в которой все последующие слова (до конца файла или объявления `.data`) интерпретируются как инициализация или резервация сегментов памяти для пользовательских данных;
- `label` -- метка, которая является указателем на адрес памяти инструкции за ней (если метка в section `.text`) или является указателем на первый элемент зарезервированого сегмента памяти (если метка в section `.data`);
- `res n` -- оператор, который может писаться после объявления метки в секции данных, обозначающий, что необходимо зарезервировать `n` слов памяти под эту метку;
- `push n` -- кладет значение `n` на вершину стэка. Если `n` - **метка, то кладет адрес**, который она описывает, если `n` - число, то кладет само значение `n`. ВАЖНО: так как у меня гарвардская архитектура, `push label` я могу выполнять **только для label из Data Memory**;
- `pop` -- удаляет верхний элемент со стэка;
- `jump label` -- команда безусловного перехода. Устанавливает следующую команду, как ту, на которую указывает label - из Program Memory; 
- `jz label` -- если на вершине стэка 0, то выполняет `jump`, иначе переход к следующей команде;
- `jnz label` -- если на вершине стэка не 0, то выполняет `jump`, иначе переход к следующей команде;
- `js label` -- если на вершине стэка отрицательное число, то выполняет `jump`, иначе переход к следующей команде;
- `jns label` -- если на вершине стэка не отрицательное число, то выполняет `jump`, иначе переход к следующей команде;
- `call label` -- сохраняет на стэке вызывов адрес следующей команды и переходит к выполнению инструкции за label;
- `ret` -- устанавливает следующую команду, как ту, что лежит на верху стэка вызовов и удаляет элемент с верхушки стэка вызовов;
- `input n` -- считывает один символ из порта n и записывает его на верх стэка;
- `output n` -- записывает в порт n значение из верхушки стэка;
- `halt` -- завершение программы;
- `add` -- складывает значение на вершине стэка и значение  следующее после вершины стэка, результат помещает на вершину стэка, операнды убираются со стэка;
- `sub` -- вычитает значение на вершине стэка и значение  следующее после вершины стэка, результат помещает на вершину стэка, операнды убираются со стэка;
- `mul` -- перемножает значение на вершине стэка и значение  следующее после вершины стэка, результат помещает на вершину стэка, операнды убираются со стэка;
- `div` -- делит значение на вершине стэка и значение  следующее после вершины стэка нацело, результат помещает на вершину стэка, операнды убираются со стэка;
- `mod` -- берёт остаток от деления значения на вершине стэка на значение следующего после вершины стэка, результат помещает на вершину стэка, операнды убираются со стэка;
- `cmp` -- вычитает значение на вершине стэка и значение  следующее после вершины стэка, результат помещает на вершину стэка, операнды НЕ убираются со стэка;
- `and` -- битовое И значения на вершине стэка и значения  следующего после вершины стэка, результат помещает на вершину стэка, операнды убираются со стэка;
- `or` -- битовое ИЛИ значения на вершине стэка и значения  следующего после вершины стэка, результат помещает на вершину стэка, операнды убираются со стэка;
- `xor` -- битовое исключающее ИЛИ значения на вершине стэка и значения  следующего после вершины стэка, результат помещает на вершину стэка, операнды убираются со стэка;
- `not` -- битовое НЕ значения на вершине стэка;
- `swap` -- меняет местами значение на вершине стэка и значение следующее после вершины стэка;
- `dup` -- кладёт на вершину стэка значение с вершине стэка;
- `over` -- кладёт на вершину стэка значение следующее после вершины стэка;
- `over3` -- кладёт на вершину стэка значение следующее после значения, следующего после вершины стэка;
- `inc` -- увеличивает значение верхушки стэка на 1;
- `dec` -- уменьшает значение верхушки стэка на 1;
- `neg` -- устанавливает значение верхушки стэка на отрицательное (* (-1));
- `load` -- интерпретирует значение на вершине стэка, как адрес по которому из памяти загружает значение на вершину стэка.
- `store` -- интерпретирует значение следующее после вершины стэка, как адрес по которому нужно записать значение на вершине стэка.
- `debug` -- команда отладки. Вывод  в устройство ввода-вывода 1 отладочную информацию о текущем значении процессора и останавливает программу до нажатия пользователем любой клавиши.
- `nop` -- пустая команда. Совершается тик, переходят к следующей инструкции.

#### Комментарии:

Начинаются со знака `;` и идут до конца строки.

#### Особенности реализации

- В программе не может быть дублирующихся меток.

- Метка памяти данных задается на той же строке, что и данные:
``` asm 
hello_world: "Hello, world!"
```

- Так как строки Pascal-string, компилятор сам упаковывает их во время компиляции (ставит первым словом строки длину строки).

- Метка памяти команд задается на строке предшествующей инструкции, на которую указывает метка, либо на той же самой строке:
```
foo:
    push 10
    ...

bar: nop
    ...
```

#### Порядок выполнения: 

Программа выполняется последовательно, одна инструкция за другой.

#### Память: 
- Распределяется статически на этапе трансляции
- Строковые литералы помещаются в память в начале работы программы в формате Pascal-string.
- Под динамически считываемые строки пользователь сам определяет, как будет считываться строка. Он может выделить некоторый буфер через `res n`, или расположить строку в конце памяти и считывать сколько необходимо (или пока хватает памяти).

#### Область видимости

В любом месте секции `.text` доступен стэк и операции над его верхними значениями. Видимость меток глобальная.

#### Типизация, виды литералов

Литералы могут быть представлены в виде чисел и меток (в последствии интерпретируются как числа), в секции `.data` можно объявлять строки. Типизация отсутсвует, так как пользователь языка может интерпретировать любые данные как захочет и может с ними выполнить любые из возможных операций.

## Организация памяти

- Гарвардская архитектура
- Резмер машинного слова:
  - Память данных - 32 бит;
  - Память команд - 32 бит.
- Имеет линейное адресное пространство.
- В памяти данных хранятся статические строки и переменных
- В памяти команд хранятся инструкции для выполнения
- Взаимодействие с памятью данных происходит при помощи инструкций `load` и `store`.
- Адресации:
  - Прямая абсолютная (например, `push label`)
  - Косвенная (у команд `load`, `store` один из операндов является указателем на ячейку памяти)

```
       Program memory
+------------------------------+
| 00 : jump n                  |
|   ...                        |
|  n : _start: instruction1    |
|   ...                        |
+------------------------------+

          Data memory
+------------------------------+
| 00  : array 1                |
|    ...                       |
|  n  : array 2                |
|    ...                       |
+------------------------------+

```

- Для работы с регистрами отведена память, организованная в виде стека. Программист напрямую имеет доступ к `TOS`, верхушке `Stack Registers`, заранее инициализированной памяти в `Data Memory`, а также, используя различные условные и безусловный переходы, может изменять `PC`;
- Память данных разделена на массивы - разделение определяет пользователь, именуя каждый массив лейблом;
- Массив может состоять из строк, чисел и свободного места (заполнено нулями), зарезервированного на определенное количество байт. Все данные в массивах и все массивы идут последовательно;
- Инструкции хранятся в `Program Memory`;
- Для операндов пользователю отводится 24 бита, т.к. предполагается, что оставшиеся 8 бит будет занимать информация о инструкции (например опкод);
- Используя команду `push number` литерал используется при помощи непосредственной адресации;   
- Используя команду `store` литерал будет загружен в статическую память;

### Стэки

- Имеются стек данных и стек возвратов.
- Оба поддерживают операции `push` и `pop`
- Стек данных поддерживает операции `dup` и `swap`, а также чтение из второй от вершины ячейки (предполагается реализация на уровне схемотехники).

### Регистры

Регистры:
- PC - счетчик команд
- AR - регистр адреса

## Система команд

**Особенности процессора:**
- Машинное слово -- знаковое 32-ух битное число;
- Доступ памяти осуществляется через указатель на вершине `Stack Register`. Установить можно при помощи `push label`;
- Устройство ввода-вывод: port-mapped
- Поток управления: 
  - Инкрементирование `PC`;
  - Условный/безусловный переход;
  - Адрес из вершины `Call Stack`.

| Команда                                                         | Число тактов | Стек ДО                                                                           | Стек ПОСЛЕ                                                                         | Описание                                                                                                                                                                                           |
|:----------------------------------------------------------------|--------------|:----------------------------------------------------------------------------------|------------------------------------------------------------------------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| PUSH [value]                                                    | 1            | <table><tr><td>...</td></tr><tr><td>...</td></tr><tr><td>...</td></tr></table>    | <table><tr><td>...</td></tr><tr><td>...</td></tr><tr><td>value</td></tr></table>   | пушит на вершину стека свой аргумент, выставляет флаги `N` (negative) и `Z` (zero) для  верхушки стека                                                                                                                                                               |
| PUSH [label]                                                    | 1            | <table><tr><td>...</td></tr><tr><td>...</td></tr><tr><td>...</td></tr></table>    | <table><tr><td>...</td></tr><tr><td>...</td></tr><tr><td>label_addr</td></tr></table>   | пушит на вершину стека свой адрес своего аргумента, выставляет флаги `N` (negative) и `Z` (zero) для  верхушки стека                                                                                                                                                               |
| LOAD                                                            | 2            | <table><tr><td>...</td></tr><tr><td>...</td></tr><tr><td>addr</td></tr></table>   | <table><tr><td>...</td></tr><tr><td>...</td></tr><tr><td>addr</td><tr><td>value</td></tr></tr></table>   | загружает значение из памяти, адрес берется из вершины стека, выставляет флаги `N` (negative) и `Z` (zero) для  верхушки стека                                                                                                                                       |
| STORE                                                           | 2            | <table><tr><td>...</td></tr><tr><td>addr</td></tr><tr><td>value</td></tr></table> | <table><tr><td>...</td></tr><tr><td>addr</td></tr><tr><td>value</td></tr></table>   | сохраняет значение из вершины стека, адрес берется из второй ячейки                                                                                                                          |
| POP                                                             | 1            | <table><tr><td>...</td></tr><tr><td>...</td></tr><tr><td>value</td></tr></table>  | <table><tr><td>...</td></tr><tr><td>...</td></tr><tr><td>...</td></tr></table>     | удаляет вершину стека, выставляет флаги `N` (negative) и `Z` (zero) для  верхушки стека                                                                                                                                                                              |
| ADD<br/>SUB<br/>MUL<br/>DIV<br/>MOD<br/>AND<br/>OR<br/>XOR<br/>MOD<br/>MOD<br/>MOD                             | 1            | <table><tr><td>...</td></tr><tr><td>a</td></tr><tr><td>b</td></tr></table>        | <table><tr><td>...</td></tr><tr><td>...</td></tr><tr><td>result</td></tr></table>  | выполняет арифметическую операцию, выставляет флаги `N` (negative) и `Z` (zero) для  верхушки стека                                                                                                                                                                  |
| CMP                             | 1            | <table><tr><td>...</td></tr><tr><td>a</td></tr><tr><td>b</td></tr></table>        | <table><tr><td>a</td></tr><tr><td>b</td></tr><tr><td>result</td></tr></table>  | выполняет a - b, сохраняет операнды, выставляет флаги `N` (negative) и `Z` (zero) для  верхушки стека                                                                                                                                                                  |
| INC<br/>DEC                                                     | 1            | <table><tr><td>...</td></tr><tr><td>...</td></tr><tr><td>value</td></tr></table>  | <table><tr><td>...</td></tr><tr><td>...</td></tr><tr><td>result</td></tr></table>  | выполняет инкремент или декремент, выставляет флаги `N` (negative) и `Z` (zero) для  верхушки стека                                                                                                                                                                  |
| INPUT [port]                                                     | 1            | <table><tr><td>...</td></tr><tr><td>...</td></tr><tr><td>...</td></tr></table>    | <table><tr><td>...</td></tr><tr><td>...</td></tr><tr><td>value</td></tr></table>   | читает из устройства ввода-вывода с порта один символ, выставляет флаги `N` (negative) и `Z` (zero) для  верхушки стека                                                                                                                                                                        |
| OUTPUT [port]                                                    | 1            | <table><tr><td>...</td></tr><tr><td>...</td></tr><tr><td>value</td></tr></table>  | <table><tr><td>...</td></tr><tr><td>...</td></tr><tr><td>value</td></tr></table>     | записывает вершину стека в порт                                                                                                                                                                    |
| DUP                                                             | 1            | <table><tr><td>...</td></tr><tr><td>...</td></tr><tr><td>value</td></tr></table>  | <table><tr><td>...</td></tr><tr><td>value</td></tr><tr><td>value</td></tr></table> | дублирует значение с вершины стека                                                                                                                                                                 |
| SWAP                                                            | 1            | <table><tr><td>...</td></tr><tr><td>a</td></tr><tr><td>b</td></tr></table>        | <table><tr><td>...</td></tr><tr><td>b</td></tr><tr><td>a</td></tr></table>         | меняет местами верхние 2 значения в стеке, выставляет флаги `N` (negative) и `Z` (zero) для  верхушки стека                                                                                                                                                          |
| OVER                                                            | 1            | <table><tr><td>...</td></tr><tr><td>a</td></tr><tr><td>b</td></tr></table>        | <table><tr><td>a</td></tr><tr><td>b</td></tr><tr><td>a</td></tr></table>         | кладёт на вершину стэка значение следующее после вершины стэка, выставляет флаги `N` (negative) и `Z` (zero) для  верхушки стека                                                                                                                                                          |
| OVER3                                                            | 1            | <table><tr><td>...</td></tr><tr><td>a</td></tr><tr><td>b</td></tr><tr><td>c</td></tr></table>        | <table><tr><td>a</td></tr><tr><td>b</td></tr><tr><td>c</td></tr><tr><td>a</td></tr></table>         | кладёт на вершину стэка значение второе после вершины стэка, выставляет флаги `N` (negative) и `Z` (zero) для  верхушки стека                                                                                                                                                          |
| JUMP [addr]<br/>JZ [addr]<br/>JNZ [addr]<br/>JS [addr]<br/>JNS [addr] | 1            | -                                                                                 | -                                                                                  | прыжок на инструкцию на основании выставленных флагов. <br/>`JUMP` - безусловный, <br/>`JZ` - прыжок, если ноль, <br/>`JNZ` - прыжок, если не ноль, <br/>`JS`/`JNS` - прыжок, если отрицательное/не отрицательное |
| CALL [addr]                                                     | 1            | -                                                                                 | -                                                                                  | вызов функции по адресу addr                                                                                                                                                                       |
| RET                                                             | 1            | -                                                                                 | -                                                                                  | возврат из функции                                                                                                                                                                                 |
| DEBUG                                                            | 1            | -                                                                                 | -                                                                                  | вывод отладочной информации на устройство на порту 1, остановка программы до действий пользователя                                                                                                                                                                              |
| NOP                                                            | 1            | -                                                                                 | -                                                                                  | пустая инструкция                                                                                                                                                                              |
| HALT                                                            | 1            | -                                                                                 | -                                                                                  | остановить выполнение                                                                                                                                                                              |

### Формат инструкций
Инструкции представлены в формате _JSON_:

```json
{
  "opcode": "jump",
  "operand": 123,
  "address": 10
}
```
где:
- `opcode` - код операции (Opcode - тип данных, определенный в [isa](./src/isa/opcode.py))
- `operand` - аргумент инструкции
- `address` - указывает адрес инструкции в памяти инструкций.

## Транслятор

Реализация транслятора: [translator](./src/translator/main.py)

Интерфейс командной строки:

- Получить справку: `poetry run translator --help`

```
usage: translator [-h] source_file target_instrs_file target_data_file
CSA Lab 3 translator.

positional arguments:
  source_file         File with asm code
  target_instrs_file  File to write instructions after compilation
  target_data_file    File to write data after compilation

options:
  -h, --help          show this help message and exit
```

`poetry run translator [-h] <source_file> <target_instrs_file> <target_data_file>`

- Первый аргумент - путь до файла с исходным кодом,
- второй аргумент - путь до файла, куда будут записаны инструкции, сохраненные в `json`.
- третий аргумент - путь до файла, куда будут записаны массивы данных, инициализированные в пользовательской программе, сохраненные в `json`.  

Трансляция секции `.data`:
- Реализована в `get_data`;
- Сначала определяется место в коде, где объявлена секция `.data`;
- Потом лейбл отделяется от данных;
- В `get_codes_from_data` данные преобразуются в последовательность чисел:
  - Функция `str2list_int` возвращает массив, в котором строка представляется как массив байт, на позициях одиночных чисел и резервирования - пустые массивы;
  - Функция `get_integers` удалят из данных строки, возвращает массив одиночных чисел и резервированной памяти;
  - Далее на пустые места вставляются одиночные числа и массивы резервирования;
  - В конце все данные выпрямляются в один итоговый массив.
  
Трансляция секции `.text`:
- `translate_without_operands`: инструкции разбиваются на токены, запоминаются номера меток. Возвращается высокоуровневая структура, описывающая инструкции;
- `translate_operands`: в джампы подставляются номера инструкций в зависимости от лейбла, в `push label` заменяются метки на адреса в памяти, проверяются ограничения на аргументы;
- Код из высокоурвневой структуры переводится в бинарный вид в функции `write_code`, определенной в `isa`

Правила:
- Не более одного определения секций `.data` и `.text`
- Одиночные числа, объявленные в `.data` должны принимать значения [-2^31; 2^31 - 1];
- Метка в секции `.data` задается на той же строке, что и данные. Данные задаются на одной строке;
- Метка в секции `.text` задается перед инструкцией, на которую он указывает;
- Обязательна метка `_start`;

## Модель процессора

Реализация модели процессора: [machne](./src/machine/main.py)

Интерфейс командной строки:

- Получить справку: `poetry run machine --help`

```
usage: machine [-h] [--log_level {FATAL,ERROR,WARN,INFO,DEBUG,NOTSET,}] [--output_ports {1,2,1;2}] instructions_file data_file input_file

CSA Lab 3 machine runner.

positional arguments:
  instructions_file     File with instructions
  data_file             File with data
  input_file            File with user input

options:
  -h, --help            show this help message and exit
  --log_level {FATAL,ERROR,WARN,INFO,DEBUG,NOTSET}
                        Log level
  --output_ports {1,2,1;2}
                        IO ports to print output
```

- Первый аргумент - путь до файла с инструкциями,
- Второй аргумент - путь до файла с данными.
- Третий аргумент - путь до файла, откуда берется ввод пользователя.  
- Опция `--log_level` - позволяет установить уровень логирования.
- Опция `--output_ports` - позволяет выбрать, с каких устройств ввода-вывода по портам данные будут также выводиться в терминал при запуске.


### Ввод-вывод

Разработаны `IOController`, который на основании порта [0-15] использует устройство ввода-вывода. Сделано несколько устройств ввода-вывода (реализация в [io.py](./src/machine/components/io.py)):
- `IO0`: ввод данных посимвольно из stdin (реализация через файл `<input_file>`). Если данные закончились, отдает EOF (-1). *Использование*: `INPUT 0`
- `IO1`: вывод ячейки в stdout как символа (для значения 97 выведет `a`). *Использование*: `OUTPUT 1`
- `IO2`: вывод ячейки в stdout как числа (для значения 97 выведет `97`). *Использование*: `OUTPUT 1`
- `IO8`: ввод данных из бесконечного потока символов `'1', ..., '9', '0', '1', ...`. Читает по одному символу из этого потока. *Использование*: `INPUT 8`


### DataPath

![data_path.svg](./img/data_path.svg)

Реализован в [data_path](src/machine/data_path.py)

Сигналы (обрабатываются за один такт, реализованы в виде методов класса)
- `latch_data_addr` - защёлкнуть значение в data_addr
- `latch_tos` - защёлкнуть вершину стека
- `store` / `load` - сигналы записи / чтения памяти данных
- `operation` - сигнал, определяющий операцию алу
- `read` / `write` / `port` - сигналы чтения / записи / порта устройства ввода вывода

Флаги:
- `Z` - zero - отражает нулевое значение в вершине стека
- `N` - negative - отражает отрицательное значение в вершине стека

### ControlUnit

![control_unit.svg](img/control_unit.svg)

Реализован в [control_unit](./src/machine/control_unit.py)
- hardwired - внутренняя логика дешифратора инструкций скрыта. В данной модели реализована на Python.
- Метод `decode_and_execute_instruction` моделирует выполнение полного цикла инструкции.
- `_tick` - имитирует работу счетчика тактов.

Сигналы: 
- `latch_pc` - защелкнуть значение в program_counter
- `read` - чтение из памяти инструкций

Особенности работы модели:
- Цикл симуляции осуществляется в функции `simulation`.
- Шаг моделирования соответствует одной инструкции с выводом состояния в журнал.
- Для журнала состояний процессора используется стандартный модуль `logging`.
- Остановка модели осуществляется при следующих условиях:
  - достижение инструкции halt;
  - переполнение стека или чтение из пустого стека;
  - отсутствие данных для чтения из порта ввода;
  - чтение или запись в несуществующий адрес памяти.
- Модель может быть остановлена и возобновлена командой `debug`.

## Тестирование

Тестирование выполняется при помощи golden test-ов.
- Конфигурация лежит в директории [tests](./tests)

GitHub Actions при совершении `push`-а автоматически
- запускает golden-тесты (задание `test`)
- проверяет форматирование Python и запускает линтеры (`ruff`)
- проверяет форматирование Markdown (`markdownlint`)

Конфигурация для GitHub Actions находится в файлах [python.yml](.github/workflows/python.yml) и [markdown.yml](.github/workflows/markdown.yml)

### Результаты тестирования:

Golden-тесты:

```
❯ poetry run coverage run -m pytest . -v
============================================================================================ test session starts ============================================================================================
platform linux -- Python 3.12.2, pytest-7.4.4, pluggy-1.5.0 -- /home/max/.cache/pypoetry/virtualenvs/csa3-stack-machine-Mqil_AOd-py3.12/bin/python
cachedir: .pytest_cache
rootdir: /home/max/prog/itmo/csa3-stack-machine
configfile: pyproject.toml
plugins: golden-0.2.2
collected 6 items                                                                                                                                                                                           

tests/golden_test.py::test_translator_and_machine[golden/prob2.yml] PASSED                                                                                                                            [ 16%]
tests/golden_test.py::test_translator_and_machine[golden/0_to_9.yml] PASSED                                                                                                                           [ 33%]
tests/golden_test.py::test_translator_and_machine[golden/cat.yml] PASSED                                                                                                                              [ 50%]
tests/golden_test.py::test_translator_and_machine[golden/hello_username.yml] PASSED                                                                                                                   [ 66%]
tests/golden_test.py::test_translator_and_machine[golden/hello_world.yml] PASSED                                                                                                                      [ 83%]
tests/golden_test.py::test_translator_and_machine[golden/string_utils.yml] PASSED                                                                                                                     [100%]

============================================================================================= 6 passed in 1.62s =============================================================================================
```

Покрытие:

```
❯ poetry run coverage report -m

Name                                        Stmts   Miss  Cover   Missing
-------------------------------------------------------------------------
src/__init__.py                                 0      0   100%
src/constants.py                                9      0   100%
src/isa/__init__.py                             6      0   100%
src/isa/data.py                                16      0   100%
src/isa/dump.py                                16      0   100%
src/isa/instruction.py                         18      1    94%   23
src/isa/json_utils.py                          15      0   100%
src/isa/memory.py                              33      0   100%
src/isa/opcode.py                              48      2    96%   56, 64
src/machine/__init__.py                         0      0   100%
src/machine/components/__init__.py              0      0   100%
src/machine/components/alu.py                  27      2    93%   50, 52
src/machine/components/call_stack.py           18      0   100%
src/machine/components/data_stack.py           48      2    96%   35-36
src/machine/components/io.py                   80      8    90%   11, 15, 29, 58, 69, 86, 109, 123
src/machine/components/memory.py               20      1    95%   21
src/machine/control_unit.py                    89      3    97%   114-117
src/machine/data_path.py                       41      0   100%
src/machine/main.py                            44     25    43%   35-45, 49-53, 57-77, 81
src/machine/simulation.py                      41      3    93%   24, 26, 31
src/main.py                                     8      3    62%   9-11
src/translator/__init__.py                      3      0   100%
src/translator/data_translator.py              82      4    95%   15-16, 104-105
src/translator/instructions_translator.py      69      2    97%   21, 35
src/translator/main.py                         34      7    79%   50-57, 61
src/translator/utils.py                        15      0   100%
tests/__init__.py                               0      0   100%
tests/golden_test.py                           32      0   100%
-------------------------------------------------------------------------
TOTAL                                         812     63    92%
```

Алгоритмы согласно варианту:
- [hello_world](./tests/golden/hello_world.yml)
- [cat](./tests/golden/cat.yml)
- [hello_username](./tests/golden/hello_username.yml)
- [prob2](./tests/golden/prob2.yml)

Дополнительные алгоритмы:
- [string_utils](./tests/golden/string_utils.yml) - набор функций для удобной работы со строками.
- [0_to_9.yml](./tests/golden/0_to_9.yml) - демонстрация работы IO8.

### Отчет на примере Hello, world

Исходный код:

```asm
.data
hello_str: "Hello, world!"

.text
_start:
        push hello_str
        load
cycle:
        jz ext
        swap
        inc
        load
        output 1
        pop
        swap
        dec
        jmp cycle
        pop
        pop
        halt
```

Машинный код:

```json
[
  {"address": 0, "opcode": "jmp", "operand": 1},
  {"address": 1, "opcode": "push", "operand": 0},
  {"address": 2, "opcode": "load", "operand": null},
  {"address": 3, "opcode": "jz", "operand": 12},
  {"address": 4, "opcode": "swap", "operand": null},
  {"address": 5, "opcode": "inc", "operand": null},
  {"address": 6, "opcode": "load", "operand": null},
  {"address": 7, "opcode": "output", "operand": 1},
  {"address": 8, "opcode": "pop", "operand": null},
  {"address": 9, "opcode": "swap", "operand": null},
  {"address": 10, "opcode": "dec", "operand": null},
  {"address": 11, "opcode": "jmp", "operand": 3},
  {"address": 12, "opcode": "pop", "operand": null},
  {"address": 13, "opcode": "pop", "operand": null},
  {"address": 14, "opcode": "halt", "operand": null}
]
```

Данные:

```json
[
  {"address": 0, "value": 13},
  {"address": 1, "value": 72},
  {"address": 2, "value": 101},
  {"address": 3, "value": 108},
  {"address": 4, "value": 108},
  {"address": 5, "value": 111},
  {"address": 6, "value": 44},
  {"address": 7, "value": 32},
  {"address": 8, "value": 119},
  {"address": 9, "value": 111},
  {"address": 10, "value": 114},
  {"address": 11, "value": 108},
  {"address": 12, "value": 100},
  {"address": 13, "value": 33}
]
```

Вывод:

```
source LoC: 20 code instr: 15
============================================================
Hello, world!

instr_counter:  123 ticks: 137
```

Журнал (не весь):

```
DEBUG   simulation:run           TICK:  70,  PC:   8,  AR:   7,  MEM_OUT:  32,  TOS: [32, 7, 7]            ,    pop       |
DEBUG   simulation:run           TICK:  71,  PC:   9,  AR:   7,  MEM_OUT:  32,  TOS: [7, 7]                ,    swap      |
DEBUG   simulation:run           TICK:  72,  PC:  10,  AR:   7,  MEM_OUT:  32,  TOS: [7, 7]                ,    dec       |
DEBUG   simulation:run           TICK:  73,  PC:  11,  AR:   7,  MEM_OUT:  32,  TOS: [6, 7]                ,    jmp 3     |
DEBUG   simulation:run           TICK:  74,  PC:   3,  AR:   7,  MEM_OUT:  32,  TOS: [6, 7]                ,    jz 12     |
DEBUG   simulation:run           TICK:  75,  PC:   4,  AR:   7,  MEM_OUT:  32,  TOS: [6, 7]                ,    swap      |
DEBUG   simulation:run           TICK:  76,  PC:   5,  AR:   7,  MEM_OUT:  32,  TOS: [7, 6]                ,    inc       |
DEBUG   simulation:run           TICK:  77,  PC:   6,  AR:   7,  MEM_OUT:  32,  TOS: [8, 6]                ,    load      |
DEBUG   simulation:run           TICK:  79,  PC:   7,  AR:   8,  MEM_OUT: 119,  TOS: [119, 8, 6]           ,    output 1  |
DEBUG   io:log_io        OUTPUT: w
DEBUG   simulation:run           TICK:  80,  PC:   8,  AR:   8,  MEM_OUT: 119,  TOS: [119, 8, 6]           ,    pop       |
DEBUG   simulation:run           TICK:  81,  PC:   9,  AR:   8,  MEM_OUT: 119,  TOS: [8, 6]                ,    swap      |
DEBUG   simulation:run           TICK:  82,  PC:  10,  AR:   8,  MEM_OUT: 119,  TOS: [6, 8]                ,    dec       |
DEBUG   simulation:run           TICK:  83,  PC:  11,  AR:   8,  MEM_OUT: 119,  TOS: [5, 8]                ,    jmp 3     |
DEBUG   simulation:run           TICK:  84,  PC:   3,  AR:   8,  MEM_OUT: 119,  TOS: [5, 8]                ,    jz 12     |
DEBUG   simulation:run           TICK:  85,  PC:   4,  AR:   8,  MEM_OUT: 119,  TOS: [5, 8]                ,    swap      |
DEBUG   simulation:run           TICK:  86,  PC:   5,  AR:   8,  MEM_OUT: 119,  TOS: [8, 5]                ,    inc       |
DEBUG   simulation:run           TICK:  87,  PC:   6,  AR:   8,  MEM_OUT: 119,  TOS: [9, 5]                ,    load      |
DEBUG   simulation:run           TICK:  89,  PC:   7,  AR:   9,  MEM_OUT: 111,  TOS: [111, 9, 5]           ,    output 1  |
DEBUG   io:log_io        OUTPUT: o
DEBUG   simulation:run           TICK:  90,  PC:   8,  AR:   9,  MEM_OUT: 111,  TOS: [111, 9, 5]           ,    pop       |
DEBUG   simulation:run           TICK:  91,  PC:   9,  AR:   9,  MEM_OUT: 111,  TOS: [9, 5]                ,    swap      |
DEBUG   simulation:run           TICK:  92,  PC:  10,  AR:   9,  MEM_OUT: 111,  TOS: [5, 9]                ,    dec       |
DEBUG   simulation:run           TICK:  93,  PC:  11,  AR:   9,  MEM_OUT: 111,  TOS: [4, 9]                ,    jmp 3     |
DEBUG   simulation:run           TICK:  94,  PC:   3,  AR:   9,  MEM_OUT: 111,  TOS: [4, 9]                ,    jz 12     |
DEBUG   simulation:run           TICK:  95,  PC:   4,  AR:   9,  MEM_OUT: 111,  TOS: [4, 9]                ,    swap      |
DEBUG   simulation:run           TICK:  96,  PC:   5,  AR:   9,  MEM_OUT: 111,  TOS: [9, 4]                ,    inc       |
DEBUG   simulation:run           TICK:  97,  PC:   6,  AR:   9,  MEM_OUT: 111,  TOS: [10, 4]               ,    load      |
DEBUG   simulation:run           TICK:  99,  PC:   7,  AR:  10,  MEM_OUT: 114,  TOS: [114, 10, 4]          ,    output 1  |
DEBUG   io:log_io        OUTPUT: r
DEBUG   simulation:run           TICK: 100,  PC:   8,  AR:  10,  MEM_OUT: 114,  TOS: [114, 10, 4]          ,    pop       |
DEBUG   simulation:run           TICK: 101,  PC:   9,  AR:  10,  MEM_OUT: 114,  TOS: [10, 4]               ,    swap      |
DEBUG   simulation:run           TICK: 102,  PC:  10,  AR:  10,  MEM_OUT: 114,  TOS: [4, 10]               ,    dec       |
DEBUG   simulation:run           TICK: 103,  PC:  11,  AR:  10,  MEM_OUT: 114,  TOS: [3, 10]               ,    jmp 3     |
DEBUG   simulation:run           TICK: 104,  PC:   3,  AR:  10,  MEM_OUT: 114,  TOS: [3, 10]               ,    jz 12     |
DEBUG   simulation:run           TICK: 105,  PC:   4,  AR:  10,  MEM_OUT: 114,  TOS: [3, 10]               ,    swap      |
DEBUG   simulation:run           TICK: 106,  PC:   5,  AR:  10,  MEM_OUT: 114,  TOS: [10, 3]               ,    inc       |
DEBUG   simulation:run           TICK: 107,  PC:   6,  AR:  10,  MEM_OUT: 114,  TOS: [11, 3]               ,    load      |
DEBUG   simulation:run           TICK: 109,  PC:   7,  AR:  11,  MEM_OUT: 108,  TOS: [108, 11, 3]          ,    output 1  |
DEBUG   io:log_io        OUTPUT: l
DEBUG   simulation:run           TICK: 110,  PC:   8,  AR:  11,  MEM_OUT: 108,  TOS: [108, 11, 3]          ,    pop       |
DEBUG   simulation:run           TICK: 111,  PC:   9,  AR:  11,  MEM_OUT: 108,  TOS: [11, 3]               ,    swap      |
DEBUG   simulation:run           TICK: 112,  PC:  10,  AR:  11,  MEM_OUT: 108,  TOS: [3, 11]               ,    dec       |
DEBUG   simulation:run           TICK: 113,  PC:  11,  AR:  11,  MEM_OUT: 108,  TOS: [2, 11]               ,    jmp 3     |
DEBUG   simulation:run           TICK: 114,  PC:   3,  AR:  11,  MEM_OUT: 108,  TOS: [2, 11]               ,    jz 12     |
DEBUG   simulation:run           TICK: 115,  PC:   4,  AR:  11,  MEM_OUT: 108,  TOS: [2, 11]               ,    swap      |
DEBUG   simulation:run           TICK: 116,  PC:   5,  AR:  11,  MEM_OUT: 108,  TOS: [11, 2]               ,    inc       |
DEBUG   simulation:run           TICK: 117,  PC:   6,  AR:  11,  MEM_OUT: 108,  TOS: [12, 2]               ,    load      |
DEBUG   simulation:run           TICK: 119,  PC:   7,  AR:  12,  MEM_OUT: 100,  TOS: [100, 12, 2]          ,    output 1  |
DEBUG   io:log_io        OUTPUT: d
DEBUG   simulation:run           TICK: 120,  PC:   8,  AR:  12,  MEM_OUT: 100,  TOS: [100, 12, 2]          ,    pop       |
DEBUG   simulation:run           TICK: 121,  PC:   9,  AR:  12,  MEM_OUT: 100,  TOS: [12, 2]               ,    swap      |
DEBUG   simulation:run           TICK: 122,  PC:  10,  AR:  12,  MEM_OUT: 100,  TOS: [2, 12]               ,    dec       |
DEBUG   simulation:run           TICK: 123,  PC:  11,  AR:  12,  MEM_OUT: 100,  TOS: [1, 12]               ,    jmp 3     |
DEBUG   simulation:run           TICK: 124,  PC:   3,  AR:  12,  MEM_OUT: 100,  TOS: [1, 12]               ,    jz 12     |
DEBUG   simulation:run           TICK: 125,  PC:   4,  AR:  12,  MEM_OUT: 100,  TOS: [1, 12]               ,    swap      |
DEBUG   simulation:run           TICK: 126,  PC:   5,  AR:  12,  MEM_OUT: 100,  TOS: [12, 1]               ,    inc       |
DEBUG   simulation:run           TICK: 127,  PC:   6,  AR:  12,  MEM_OUT: 100,  TOS: [13, 1]               ,    load      |
DEBUG   simulation:run           TICK: 129,  PC:   7,  AR:  13,  MEM_OUT:  33,  TOS: [33, 13, 1]           ,    output 1  |
DEBUG   io:log_io        OUTPUT: !
DEBUG   simulation:run           TICK: 130,  PC:   8,  AR:  13,  MEM_OUT:  33,  TOS: [33, 13, 1]           ,    pop       |
DEBUG   simulation:run           TICK: 131,  PC:   9,  AR:  13,  MEM_OUT:  33,  TOS: [13, 1]               ,    swap      |
DEBUG   simulation:run           TICK: 132,  PC:  10,  AR:  13,  MEM_OUT:  33,  TOS: [1, 13]               ,    dec       |
DEBUG   simulation:run           TICK: 133,  PC:  11,  AR:  13,  MEM_OUT:  33,  TOS: [0, 13]               ,    jmp 3     |
DEBUG   simulation:run           TICK: 134,  PC:   3,  AR:  13,  MEM_OUT:  33,  TOS: [0, 13]               ,    jz 12     |
DEBUG   simulation:run           TICK: 135,  PC:  12,  AR:  13,  MEM_OUT:  33,  TOS: [0, 13]               ,    pop       |
DEBUG   simulation:run           TICK: 136,  PC:  13,  AR:  13,  MEM_OUT:  33,  TOS: [13]                  ,    pop       |
DEBUG   simulation:run           TICK: 137,  PC:  14,  AR:  13,  MEM_OUT:  33,  TOS: []                    ,    halt      |
DEBUG   simulation:simulation    memory: DATA: [
    0:     13
    1:     72
    2:     101
    3:     108
    4:     108
    5:     111
    6:     44
    7:     32
    8:     119
    9:     111
    10:    114
    11:    108
    12:    100
    13:    33
]
INFO    simulation:simulation    output_buffer (port 1): 'Hello, world!'
INFO    simulation:simulation    output_buffer (port 2): ''
```

### Статистика по алгоритмам

```text
| ФИО                        | алг            | LoC | code инстр. | инстр. | такт. |
| Барсуков Максим Андреевич  | cat            | 47  | 38          | 198    | 234   |
| Барсуков Максим Андреевич  | hello_world    | 20  | 15          | 123    | 137   |
| Барсуков Максим Андреевич  | hello_username | 86  | 60          | 677    | 774   |
| Барсуков Максим Андреевич  | prob2          | 69  | 44          | 513    | 597   |
```
