from __future__ import annotations

from datetime import datetime
from pathlib import Path
import shutil
import subprocess
import sys

PACKAGE = Path(__file__).resolve().parent
PROJECT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd().resolve()

required = [
    PROJECT / "apps" / "api" / "app",
    PROJECT / "apps" / "web" / "app",
]
if not all(path.exists() for path in required):
    raise SystemExit(
        "Run this from the edgeboard-v3 root, or pass the repository path.\n"
        "Example: python install_consolidated.py C:\\Users\\YourName\\edgeboard-v3"
    )

backup = PROJECT / f"_backup_before_m3_1_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
backup.mkdir(parents=True, exist_ok=True)

def copy_tree_with_backup(source: Path, destination: Path) -> None:
    for source_file in source.rglob("*"):
        if not source_file.is_file():
            continue
        relative = source_file.relative_to(source)
        target = destination / relative
        if target.exists():
            backup_target = backup / target.relative_to(PROJECT)
            backup_target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(target, backup_target)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_file, target)

print("1/4 Installing admin views, friend invites, and shared API files...")
copy_tree_with_backup(PACKAGE / "payload", PROJECT)

print("2/4 Installing structured pick reasoning and best-line grouping...")
subprocess.run(
    [sys.executable, str(PACKAGE / "scripts" / "install_pick_reasoning.py"), str(PROJECT)],
    check=True,
)

print("3/4 Installing pipeline upserts, deduplication, and error handling...")
subprocess.run(
    [sys.executable, str(PACKAGE / "scripts" / "patch_pipeline_stability.py"), str(PROJECT)],
    check=True,
)

print("4/4 Installing scheduler retries and the System Health dashboard...")
copy_tree_with_backup(PACKAGE / "phase31_replacements", PROJECT)

print()
print("Consolidated EdgeBoard Milestone 3.1 installation completed.")
print(f"Backup created at: {backup}")
print("Commit and push, wait for Render, log back in, then run Full refresh from /admin.")
