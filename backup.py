import shutil
import logging
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Iterator, Tuple

SRC_PATHS = [
    Path("C:/Users/louis/Documents/"),
    Path("C:/Users/louis/Pictures/"),
    Path("C:/Users/louis/Music/"),
    Path("C:/Users/louis/Videos/"),
]
DST_PATH = Path("D:/backup/").expanduser().resolve()
INTERVAL = timedelta(hours=6)


logging.basicConfig(
    format="[{asctime}] {levelname:<8} - {message}",
    style="{",
    datefmt="%H:%M:%S",
    level=logging.DEBUG,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("backup.log", mode="w"),
    ],
)


def files_to_backup_from(src_root: Path, dst_root: Path) -> Iterator[Tuple[Path, Path]]:
    for src_path in src_root.rglob("*"):
        if not src_path.is_file():
            continue

        rel_path = src_path.relative_to(src_root)
        dst_path = dst_root / src_root.name / rel_path

        if dst_path.exists():
            src_mtime = datetime.fromtimestamp(src_path.stat().st_mtime)
            dst_mtime = datetime.fromtimestamp(dst_path.stat().st_mtime)
            if src_mtime - dst_mtime < INTERVAL:
                continue

        yield src_path, dst_path


logging.info("Checking available space and backup size...")

backup_size = 0
file_count = 0
for root in SRC_PATHS:
    size = 0
    for src_path, _ in files_to_backup_from(root, DST_PATH):
        size += src_path.stat().st_size
        file_count += 1
    backup_size += size

available_space = shutil.disk_usage(DST_PATH).free

if file_count == 0:
    logging.info("No files found to backup, exiting...")
    sys.exit()

logging.info(f"Found {file_count} file(s) to back up")
logging.info(f"Size of back up: {backup_size} Bytes")
logging.info(f"Available size: {available_space} Bytes")

if backup_size >= available_space:
    message = f"Not enough disk space available for the backup. Required {backup_size}, available {available_space}"
    logging.error(message)
    raise MemoryError(message)

logging.info("Starting backup...")

for SRC_PATH in SRC_PATHS:
    for src_path, dst_path in files_to_backup_from(SRC_PATH, DST_PATH):
        try:
            dst_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src_path, dst_path)
        except Exception as e:
            logging.error(f"Failed to back up {src_path}: {e}")
        logging.info(f"Backed up: {src_path}")
