import shutil
import logging
import sys
from pathlib import Path
from datetime import datetime, timedelta

SRC_PATHS = [
    Path("C:/Users/louis/Documents/"),
    Path("C:/Users/louis/Pictures/"),
    Path("C:/Users/louis/Music/"),
    Path("C:/Users/louis/Videos/"),
]
DST_PATH = Path("D:/backup/").expanduser().resolve()
INTERVAL = timedelta(hours=6)

available_space = shutil.disk_usage(DST_PATH).free
print(shutil.disk_usage(SRC_PATHS[0]))

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

size = 0
for SRC_PATH in SRC_PATHS:
    for src_path in SRC_PATH.rglob("*"):
        if src_path.is_file():
            size += src_path.stat().st_size
    print(f"{size=}")

logging.info("Starting backup...")

for SRC_PATH in SRC_PATHS:
    for src_path in SRC_PATH.rglob("*"):

        if not src_path.is_file():
            continue

        rel_path = src_path.relative_to(SRC_PATH)
        dst_path = DST_PATH / SRC_PATH.name / rel_path
        dst_path.parent.mkdir(parents=True, exist_ok=True)

        if dst_path.exists():
            src_mtime = datetime.fromtimestamp(src_path.stat().st_mtime)
            dst_mtime = datetime.fromtimestamp(dst_path.stat().st_mtime)
            if src_mtime - dst_mtime < INTERVAL:
                continue

        logging.info(f"Backing up: {src_path}")
        shutil.copy2(src_path, dst_path)
