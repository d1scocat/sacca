import subprocess
import sys


def main():
    fix = "--fix" in sys.argv
    cmd = ["ruff", "check", "src", "tests"]
    if fix:
        cmd.append("--fix")

    try:
        result = subprocess.run(
            args=cmd,
            check=False,
            capture_output=False
        )
        if result.returncode == 0:
            print("✅ No lint errors found")
        sys.exit(result.returncode)
    except FileNotFoundError:
        print("⚠️ Ruff not found. Please install it in your environment.")
        sys.exit(1)

if __name__ == "__main__":
    main()
