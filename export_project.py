
import os
from pathlib import Path

# ==================================================
# CONFIGURATION
# ==================================================

# Root Folder ของ Project (ตำแหน่งที่วาง Script นี้)
PROJECT_ROOT = Path(__file__).resolve().parent

# ไฟล์ผลลัพธ์
OUTPUT_FILE = PROJECT_ROOT / "Project_Export.txt"

# Folder ที่ต้องการยกเว้น (ไม่รวม Subfolder ภายในด้วย)
EXCLUDED_DIRS = {
    "SETUP",
    ".git",
    "__pycache__",
    ".venv",
    "venv",
    "env",
    "node_modules",
    ".idea",
    ".vscode",
}

# นามสกุลไฟล์ที่ต้องการ Export
# เพิ่มหรือลบรายการได้ตามต้องการ
ALLOWED_EXTENSIONS = {
    ".py",
    ".html",
    ".htm",
    ".css",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".json",
    ".sql",
    ".md",
    ".txt",
    ".yaml",
    ".yml",
    ".toml",
    ".ini",
    ".cfg",
    ".conf",
    ".bat",
    ".ps1",
    ".sh",
    ".env.example",
    ".gitignore",
    ".dockerignore",
    ".xml",
    ".csv",
    ".ipynb",
}

# จำกัดขนาดไฟล์ข้อความต่อไฟล์ (10 MB)
MAX_FILE_SIZE = 10 * 1024 * 1024


# ==================================================
# HELPER FUNCTIONS
# ==================================================

def is_excluded_dir(dirname: str) -> bool:
    """ตรวจสอบ Folder ที่ไม่ต้องการ Export"""
    excluded = {name.lower() for name in EXCLUDED_DIRS}
    return dirname.lower() in excluded


def is_allowed_file(file_path: Path) -> bool:
    """ตรวจสอบนามสกุลไฟล์ที่อนุญาต"""
    name = file_path.name.lower()

    # รองรับชื่อไฟล์พิเศษ เช่น .gitignore
    special_names = {
        ".gitignore",
        ".dockerignore",
        ".env.example",
    }

    if name in special_names:
        return True

    return file_path.suffix.lower() in ALLOWED_EXTENSIONS


def is_binary_file(file_path: Path) -> bool:
    """ตรวจสอบไฟล์ Binary จากข้อมูลภายในไฟล์"""
    try:
        with file_path.open("rb") as file:
            sample = file.read(8192)

        return b"\0" in sample

    except OSError:
        return True


def collect_files():
    """รวบรวมไฟล์ที่ตรงเงื่อนไขทั้งหมด"""

    collected = []

    for current_root, dirs, files in os.walk(PROJECT_ROOT):
        # ยกเว้น Folder ที่กำหนด
        dirs[:] = sorted(
            dirname
            for dirname in dirs
            if not is_excluded_dir(dirname)
        )

        for filename in sorted(files):
            file_path = Path(current_root) / filename

            # ไม่รวมไฟล์ Export ตัวเอง
            if file_path.resolve() == OUTPUT_FILE.resolve():
                continue

            # ตรวจสอบนามสกุลไฟล์
            if not is_allowed_file(file_path):
                continue

            collected.append(file_path)

    return sorted(
        collected,
        key=lambda path: str(path.relative_to(PROJECT_ROOT)).lower()
    )


# ==================================================
# EXPORT PROJECT
# ==================================================

def export_project():
    files = collect_files()

    with OUTPUT_FILE.open(
        "w",
        encoding="utf-8",
        newline="\n"
    ) as output:

        # ------------------------------------------
        # PROJECT INFORMATION
        # ------------------------------------------

        output.write("PROJECT EXPORT\n")
        output.write("=" * 80 + "\n")
        output.write(f"Project Root: {PROJECT_ROOT}\n")
        output.write(f"Total Files: {len(files)}\n")
        output.write("=" * 80 + "\n\n")

        # ------------------------------------------
        # PROJECT TREE
        # ------------------------------------------

        output.write("PROJECT TREE\n")
        output.write("=" * 80 + "\n")

        output.write(f"{PROJECT_ROOT.name}/\n")

        tree = {}

        for file_path in files:
            relative_path = file_path.relative_to(PROJECT_ROOT)
            parts = relative_path.parts

            current = tree

            for part in parts:
                current = current.setdefault(part, {})

        def write_tree(node, depth=1):
            for name in sorted(node, key=str.lower):
                is_directory = bool(node[name])

                if is_directory:
                    output.write(
                        "    " * depth + name + "/\n"
                    )
                    write_tree(node[name], depth + 1)
                else:
                    output.write(
                        "    " * depth + name + "\n"
                    )

        write_tree(tree)

        # ------------------------------------------
        # FILE CONTENTS
        # ------------------------------------------

        output.write("\n\n")
        output.write("FILE CONTENTS\n")
        output.write("=" * 80 + "\n\n")

        for file_path in files:
            output.write("#" + str(file_path.resolve()) + "\n")
            output.write("-" * 80 + "\n")

            try:
                # จำกัดขนาดไฟล์เพื่อป้องกันไฟล์ใหญ่เกินไป
                file_size = file_path.stat().st_size

                if file_size > MAX_FILE_SIZE:
                    output.write(
                        f"[Skipped: file exceeds "
                        f"{MAX_FILE_SIZE // (1024 * 1024)} MB]\n"
                    )
                    output.write("\n" + "=" * 80 + "\n\n")
                    continue

                if is_binary_file(file_path):
                    output.write("[Binary file skipped]\n")
                else:
                    # อ่าน UTF-8 ก่อน แล้วลอง Windows encoding
                    try:
                        content = file_path.read_text(
                            encoding="utf-8-sig"
                        )
                    except UnicodeDecodeError:
                        content = file_path.read_text(
                            encoding="cp1252"
                        )

                    output.write(content)

                    if content and not content.endswith("\n"):
                        output.write("\n")

            except (OSError, UnicodeError) as error:
                output.write(
                    f"[File read error: {error}]\n"
                )

            output.write("\n")
            output.write("=" * 80 + "\n\n")

    print("Export completed successfully!")
    print(f"Project Root : {PROJECT_ROOT}")
    print(f"Total Files  : {len(files)}")
    print(f"Output File  : {OUTPUT_FILE}")


# ==================================================
# MAIN
# ==================================================

if __name__ == "__main__":
    export_project()
