# TX PROGRAMMING LANGUAGE
### Many dream of making their own programming language - this one's mine
TX is a structured programming language built on top of Python but introduces brackets and strict type declarations. TX supports custom modules (.tx files) and Python library and script imports.
#### Get syntax highlighting in VSCode: Ctrl + Shift + P -> Install extension from location -> select tx-syntax!

Features

    Static Typing (int, float, bool, str, list, dict, tuple, obj)

    Modular Structure with .tx modules and Python-backed libraries

    Control Flow using if, else if, else, while, for, and range

    String & List Utilities from the standard library (std)

    File I/O with flush, read, write, and close operations

    Library & Module System to import Python scripts or .tx files
    
    Built-in Type Conversion using changetype

Native Syntax Overview
### To see a full example file, check out [docs.tx here!](https://github.com/Typhoonz0/tx-language/blob/main/docs.tx)

Entry Point
```
fn main {
    # runs first, no arguments, no colon needed
}
```
Imports
```
import library libraries.stdio as std
import library os
import module helper.tx
```
Variables
```
int age = 17
str name = "Liam"
bool cool = True
list numbers = [1, 2, 3]
dict mapping = {
    "hello" :: "world",
    "python" :: "rocks",
dict }
tuple coords = (1, 2, (3, 4))
```
Functions
```
fn greet ; str name {
    std.out: "Hello, "; name; "!\n"
}
```
Loops
```
for ; i ; range 5 {
    std.out: i
}

for ; name ; in ; names {
    std.out: name
}
while ; condition {
    # do stuff
}
```
Conditionals
```
if ; x > 0 {
    std.out: "Positive"
}
else if ; x == 0 {
    std.out: "Zero"
}
else {
    std.out: "Negative"
}
```

Standard Library Highlights

Print to console:
```
std.out: "Hello"; name; "\n"
```
Operate on files:
```
obj f = std.file.open: "test.txt"; "w"
std.file.write: "Hello"; f
std.file.flush: f
std.file.close: f
```
Operate on strings:
```
str cleaned = std.string.strip: "  word  "
```
Operate on lists:
```
std.list.append: mylist; value
std.list.sort: mylist
```
