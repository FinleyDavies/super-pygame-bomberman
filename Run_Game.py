import pip
import subprocess
import os

def run_game():
    subprocess.call(["python", os.path.join("main", "client_test.py")])

def install(package):
    if hasattr(pip, "main"):
        pip.main(["install", package])
    else:
        pip._internal.main(["install", package])

# Example
if __name__ == '__main__':
    install("pygame")
    run_game()