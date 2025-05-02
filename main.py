import re
import sys
import os
import argparse
import subprocess
sys.dont_write_bytecode = True
VERSION = "0.3.0"
global subfiles
def compiler(code, inputPath, moduleMode=False):
    global subfiles
    output = []
    brace_stack = []
    # WE DO NOT WONT __pycache__!!!!!!
    output.append("import sys")
    output.append("sys.dont_write_bytecode = True")

    # For every line in the code, we need to compile it.
    for lineNumber, line in enumerate(code.splitlines(), start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        # Unlike our language, we need to add indentation
        indent = " " * (len(line) - len(line.lstrip()))

        try:
            # Import library
            if stripped.startswith("import library"):
                parts = stripped.split()
                if "as" in parts:
                    modIndex = parts.index("library") + 1
                    asIndex = parts.index("as")
                    fullMod = parts[modIndex]
                    alias = parts[asIndex + 1]
                    output.append(f"{indent}import {fullMod} as {alias}")
                else:
                    fullMod = parts[-1]
                    output.append(f"{indent}import {fullMod}")


            # Import module 
            elif stripped.startswith("import module"):
                modFile = stripped.split()[-1]
                modName = os.path.splitext(os.path.basename(modFile))[0]
                output.append(f"{indent}import {modName}")

                modulePath = os.path.join(os.path.dirname(inputPath), modFile)
                moduleOutput = modulePath.replace(".tx", ".py")
                if True:
                    print(f"[+] Compiling module {modFile} → {moduleOutput}")
                    subfiles.append(moduleOutput)
                    compileFile(modulePath, moduleOutput, isModule=True)
                else:
                    print(f"[!] Module file {modFile} not found!")
            elif stripped == "dict }":
                output.append(indent+"}")

            elif stripped.startswith("while ;") and (stripped.endswith("{") or stripped.endswith(": {")):
                condition = re.sub(r'\s*:? *\{$', '', stripped[7:].strip())
                if not condition:
                    raise SyntaxError("Missing condition in while loop")
                output.append(f"{indent}while {condition}:")
                brace_stack.append("block")
            # fn myfunc ; type arg ; type arg {
            elif stripped.startswith("fn ") and stripped.endswith("{"):
                fnDecl = stripped[3:-1].strip() 
                parts = [p.strip() for p in fnDecl.split(";") if p.strip()]
                
                funcName = parts[0]
                args = []

                for arg in parts[1:]:
                    if " " in arg:
                        _, name = arg.split()
                        args.append(name)
                    else:
                        args.append(arg)  

                argStr = ", ".join(args)
                output.append(f"{indent}def {funcName}({argStr}):")
                brace_stack.append("block")

            # else if
            elif stripped.startswith("else if ;") and stripped.endswith("{"):
                condition = stripped[10:-1].strip()
                output.append(f"{indent}elif {condition}:")
                brace_stack.append("block")

            # else
            elif stripped.startswith("else") and stripped.endswith("{"):
                output.append(f"{indent}else:")
                brace_stack.append("block")

            elif "changetype" in stripped:
                tok = stripped.split()

                # sys.exit()
                output.append(f"{indent}{tok[0]} = {tok[5]}({tok[3]})")

            # if ; condition {
            elif stripped.startswith("if ;") and stripped.endswith("{"):
                condition = stripped[4:-1].strip()
                output.append(f"{indent}if {condition}:")
                brace_stack.append("block")
            # while ; init ; condition {
            elif stripped.startswith("while ;") and stripped.endswith("{"):
                parts = stripped[7:-1].split(";")
                if len(parts) == 2:
                    init, condition = map(str.strip, parts)
                    if re.match(r"(int|float|str|bool|list|obj|dict|tuple) \w+ *=.*", init):
                        varType, rest = init.split(None, 1)
                        name, value = map(str.strip, rest.split("=", 1))
                        output.append(f"{indent}{name} = {value}")
                    else:
                        output.append(f"{indent}{init}")
                    output.append(f"{indent}while {condition}:")
                    brace_stack.append("block")
                else:
                    raise SyntaxError("Invalid while syntax")
            elif stripped.startswith("for ;") and (stripped.endswith("{") or stripped.endswith(": {")):
                clean_line = re.sub(r'\s*:? *\{$', '', stripped[5:].strip())
                parts = [p.strip() for p in clean_line.split(";")]
               # print(parts)
                # for ; int i = 0 ; range 5 { OR for ; i ; range 5 {
                if "range" in parts[1]:
                    range_expr = parts[1]
                    range_target = range_expr.replace("range", "").strip()

                    if "=" in parts[0]:
                        # Case: int i = 0
                        decl = parts[0]
                        if re.match(r"(int|float) \w+ *=.*", decl):
                            _, rest = decl.split(None, 1)
                            var_name, var_value = map(str.strip, rest.split("=", 1))
                            output.append(f"{indent}{var_name} = {var_value}")
                            output.append(f"{indent}for {var_name} in range({var_value}, {range_target}):")
                            brace_stack.append("block")
                        else:
                            raise SyntaxError("Invalid declaration in for-range loop")
                    else:
                        # Case: i ; range 5
                       # print("E")
                        var_name = parts[0]
                        output.append(f"{indent}for {var_name} in range({range_target}):")
                        brace_stack.append("block")

                        
                # for ; j ; in ; xlist {
                elif len(parts) == 3 and parts[1] == "in" and not "=" in parts[0]:
                    var_name = parts[0]
                    iterable = parts[2]

                    if not iterable.endswith("()") and "." in iterable:
                        iterable += "()"

                    output.append(f"{indent}for {var_name} in {iterable}:")
                    brace_stack.append("block")
                # for ; int j = 0 ; in ; xlist {
                elif "=" in parts[0]:
                   # print(parts)
                    decl = parts[0]
                    iterable = parts[2]

                    if re.match(r"(int|float|str|bool|list) \w+ *=.*", decl):
                        _, rest = decl.split(None, 1)
                        var_name, var_value = map(str.strip, rest.split("=", 1))
                        output.append(f"{indent}{var_name} = {var_value}")
                        if not iterable.endswith("()") and "." in iterable:
                            iterable += "()"
                        output.append(f"{indent}{var_name} = {var_value}")

                        output.append(f"{indent}for {var_name} in {iterable}:")
                        brace_stack.append("block")
                    else:
                        raise SyntaxError("Invalid variable declaration in for-loop")


            # Assignment from function call: type name = func :
            elif re.match(r"(int|float|str|bool|list|obj|dict|tuple) \w+ *=.*:", stripped):
                varType, rest = stripped.split(None, 1)
                name, call_expr = map(str.strip, rest.split("=", 1))
                
                funcCall, rawArgs = map(str.strip, call_expr.split(":", 1))
                args = ", ".join(arg.strip() for arg in rawArgs.split(";")) if rawArgs else ""
                
                output.append(f"{indent}{name} = {funcCall}({args})")

            # Variable declarations
            elif re.match(r"(int|float|str|bool|list|obj|dict|tuple) \w+ *=.*", stripped):
                varType, rest = stripped.split(None, 1)
                name, value = map(str.strip, rest.split("=", 1))
                output.append(f"{indent}{name} = {value}")

            # Function or method call
            elif ":" in stripped:
                if "::" not in stripped:
                    funcCall, rawArgs = map(str.strip, stripped.split(":", 1))
                    args = ", ".join(arg.strip() for arg in rawArgs.split(";"))
                  #  print(args)
                    output.append(f"{indent}{funcCall}({args})")
                else:
                    funcCall, rawArgs = map(str.strip, stripped.split(":", 1))
                    args = ", ".join(arg.strip() for arg in rawArgs.split(";"))
                   # print(args)
                    output.append(f"{indent}{funcCall}{args}")

            # break / continue
            elif stripped in ("break", "continue", "pass"):
                output.append(f"{indent}{stripped}")

            # Closing brace
            elif stripped == "}":
                if brace_stack:
                    brace_stack.pop()
                continue  # No output for closing brace

            # Default passthrough
            else:
                output.append(f"{indent}{stripped}")

        except Exception as e:
            print(f"[Error] Line {lineNumber}: {stripped}")
            print(f"        → {e}")
            sys.exit(1)

    if not moduleMode:
        output.append("main()")

    return "\n".join(output)


def compileFile(inputPath, outputPath=None, isModule=False, addShebang=False):
    global subfiles
    with open(inputPath) as f:
        sourceCode = f.read()

    compiledCode = compiler(sourceCode, inputPath, moduleMode=isModule)

    if outputPath:
        with open(outputPath, "w") as f:
            if addShebang:
                f.write("#!/usr/bin/env python3\n")
            f.write(compiledCode)

        if addShebang:
            os.chmod(outputPath, 0o755)
    else:
        print(compiledCode)


def main():
    global subfiles
    subfiles = []
    parser = argparse.ArgumentParser(description="tx → Python Compiler")
    parser.add_argument("source", nargs="?",help="Source .tx file")
    parser.add_argument("-o", "--output", help="Output .py file")
    parser.add_argument("--no-run", action="store_true", help="Don't run the compiled file")
    parser.add_argument("--keep", action="store_true", help="Keep .py output file")
    parser.add_argument("--version", action="store_true", help="Show compiler version")
    parser.add_argument("--unix-shell-script", action="store_true", help="Add shebang line and chmod +x for shell execution")

    args = parser.parse_args()

    if args.version:
        print(f"tx Compiler v{VERSION}")
        sys.exit(0)

    sourcePath = args.source
    outputPath = args.output or sourcePath.replace(".tx", ".py")

    compileFile(
        inputPath=sourcePath,
        outputPath=outputPath,
        isModule=False,
        addShebang=args.unix_shell_script
    )

    if not args.no_run:
        print(f"[•] Running {outputPath}...\n")
        subprocess.run(["python3", outputPath])

    if not args.keep and not args.unix_shell_script:
        try:
            os.remove(outputPath)
            for f in subfiles:
                os.remove(f)
        except FileNotFoundError:
            pass

if __name__ == "__main__":
    main()