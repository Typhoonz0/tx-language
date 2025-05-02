# Standard library for the tx programming language not included in the compiler
import sys, builtins
sys.dont_write_bytecode = True

def out(*args):
    if len(args) == 1:
        print(*args, end='')
    else:
        for i in args:
            print(i, end='')

def input(prompt=""): 
    return builtins.input(prompt)

class file:
    def open(path, mode): return open(path, mode)
    def write(data, fd): fd.write(data)
    def read(fd): return fd.read()
    def flush(fd): fd.flush()
    def close(fd): fd.close()


class string:
    def set(_, value): return value
    def get(value): return value
    def replace(value, old, new): return value.replace(old, new)
    def join(sep, iterable): return sep.join(iterable)
    def upper(value): return value.upper()
    def lower(value): return value.lower()
    def strip(value): return value.strip()
    def split(value, sep=None): return value.split(sep)


class list:
    def append(value, data): return value.append(data)
    def extend(value, data): return value.extend(data)
    def sort(value): return value.sort()
    def reverse(value): return value.reverse()
    def pop(value): return value.pop()
