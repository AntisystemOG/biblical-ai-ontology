"""Check NY weather positions and market prices for Aug 31."""
import json, sys
sys.path.insert(0, r"C:\AI Projects\Prediction Market\Kalshi\Kalshi Edge Scanner")

# Try to import the engine which likely has the Kalshi client
try:
    from engine import *
except:
    pass

# Try scanner
try:
    from scanner import *
except:
    pass

# Let's check what's in digest.py for API access
import importlib.util
spec = importlib.util.spec_from_file_location("digest", r"C:\AI Projects\Prediction Market\Kalshi\Kalshi Edge Scanner\digest.py")
digest_mod = importlib.util.module_from_spec(spec)

# Don't execute - just check what classes/functions exist
import ast
with open(r"C:\AI Projects\Prediction Market\Kalshi\Kalshi Edge Scanner\digest.py", "r") as f:
    tree = ast.parse(f.read())

for node in ast.walk(tree):
    if isinstance(node, (ast.Import, ast.ImportFrom)):
        for alias in node.names:
            print(f"Import: {alias.name}")
    elif isinstance(node, ast.ClassDef):
        print(f"Class: {node.name}")
    elif isinstance(node, ast.FunctionDef) and node.col_offset == 0:
        print(f"Function: {node.name}")