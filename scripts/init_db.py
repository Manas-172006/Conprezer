import subprocess
import sys

from _common import BACKEND_DIR


def main() -> None:
    subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=BACKEND_DIR,
        check=True,
    )
    print("DB migrated")


if __name__ == "__main__":
    main()
