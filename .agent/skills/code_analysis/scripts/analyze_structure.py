import ast
import os
import sys

def analyze_complexity(node):
    """Estimate Cyclomatic Complexity"""
    complexity = 1
    for child in ast.walk(node):
        if isinstance(child, (ast.If, ast.While, ast.For, ast.Assert, ast.ExceptHandler, ast.With, ast.Try)):
            complexity += 1
        elif isinstance(child, ast.BoolOp):
            complexity += len(child.values) - 1
    return complexity

def analyze_file(filepath):
    print(f"\nAnalyzing: {os.path.basename(filepath)}")
    print("-" * 40)
    
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        
        tree = ast.parse(content)
        
        # Imports
        imports = [n.names[0].name for n in ast.walk(tree) if isinstance(n, ast.Import)]
        import_froms = [f"{n.module}.{n.names[0].name}" for n in ast.walk(tree) if isinstance(n, ast.ImportFrom) and n.module]
        print(f"Imports: {', '.join(imports + import_froms)}")

        # Classes and Functions
        for node in tree.body:
            if isinstance(node, ast.ClassDef):
                print(f"\n[C] Class: {node.name}")
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        idx = analyze_complexity(item)
                        args = [a.arg for a in item.args.args]
                        print(f"    [M] {item.name}({', '.join(args)}) - Complexity: {idx}")
            elif isinstance(node, ast.FunctionDef):
                idx = analyze_complexity(node)
                args = [a.arg for a in node.args.args]
                print(f"\n[F] Function: {node.name}({', '.join(args)}) - Complexity: {idx}")

    except Exception as e:
        print(f"Error reading file: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python analyze_structure.py <file1> <file2> ...")
        sys.exit(1)
    
    for file_path in sys.argv[1:]:
        if os.path.exists(file_path):
            analyze_file(file_path)
        else:
            print(f"File not found: {file_path}")
