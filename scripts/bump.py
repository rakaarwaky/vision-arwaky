import os
import re
import subprocess
import sys

def bump_version(current_version):
    parts = current_version.split('.')
    if len(parts) == 3:
        try:
            parts[2] = str(int(parts[2]) + 1)
            return '.'.join(parts)
        except ValueError:
            pass
    return current_version + ".1"

def run_command(cmd):
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
    return result

def main():
    pyproject_path = os.path.join(os.path.dirname(__file__), "..", "pyproject.toml")
    if not os.path.exists(pyproject_path):
        print("pyproject.toml not found")
        sys.exit(1)
    
    with open(pyproject_path, 'r') as f:
        content = f.read()
    
    match = re.search(r'version\s*=\s*"(.*?)"', content)
    if not match:
        print("Could not find version in pyproject.toml")
        sys.exit(1)
    
    old_version = match.group(1)
    new_version = bump_version(old_version)
    
    new_content = re.sub(r'version\s*=\s*".*?"', f'version = "{new_version}"', content, count=1)
    with open(pyproject_path, 'w') as f:
        f.write(new_content)
    
    print(f"Bumped version: {old_version} -> {new_version}")
    
    # Git operations
    run_command(["git", "add", pyproject_path])
    status = run_command(["git", "status", "--porcelain"])
    if status.stdout.strip():
        run_command(["git", "commit", "--no-verify", "-m", f"chore: bump version to {new_version}"])
        run_command(["git", "push"])
    else:
        print("No changes to commit")

if __name__ == "__main__":
    main()
