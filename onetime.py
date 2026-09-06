from datetime import datetime
from pathlib import Path
import json
import re
import shutil
import sys


SEGMENTATION_ROOT = Path(
    r"C:\paprika\results\segmentation"
)

LEGACY_ROOT = Path(
    r"C:\paprika\results\leaf_segmentation"
)


TIMESTAMP_PATTERN = re.compile(
    r"_\d{8}_\d{6}(?:_\d+)?$"
)


def safe_name(name):
    name = Path(name).stem

    name = re.sub(
        r"[^A-Za-z0-9_-]+",
        "_",
        name
    )

    name = name.strip("_")

    if not name:
        name = "segmentation"

    return name


def get_timestamp(path):
    timestamp = path.stat().st_mtime

    return datetime.fromtimestamp(
        timestamp
    )


def format_timestamp(timestamp):
    return timestamp.strftime(
        "%Y%m%d_%H%M%S"
    )


def format_display_date(timestamp):
    return timestamp.strftime(
        "%d/%m/%Y %H:%M:%S"
    )


def is_new_run_structure(path):
    if not path.is_dir():
        return False

    required_directories = (
        "original",
        "masks",
        "leaves",
        "overlay",
    )

    return all(
        (path / directory).is_dir()
        for directory in required_directories
    )


def has_timestamp_in_name(name):
    return bool(
        TIMESTAMP_PATTERN.search(name)
    )


def target_directory(
    root,
    base_name,
    timestamp
):
    timestamp_text = format_timestamp(
        timestamp
    )

    base_name = safe_name(
        base_name
    )

    candidate = (
        root
        / f"{base_name}_{timestamp_text}"
    )

    counter = 1

    while candidate.exists():

        candidate = (
            root
            / f"{base_name}_{timestamp_text}_{counter:02d}"
        )

        counter += 1

    return candidate


def create_metadata(
    run_directory,
    source_file,
    source_path,
    saved_at,
    original_folder_name,
    migrated_from
):
    metadata = {
        "source_file": source_file,
        "source_path": source_path,
        "saved_at": saved_at.isoformat(
            timespec="seconds"
        ),
        "saved_at_display": format_display_date(
            saved_at
        ),
        "migrated": True,
        "original_folder_name": original_folder_name,
        "migrated_from": migrated_from,
    }

    metadata_path = (
        run_directory
        / "metadata.json"
    )

    with metadata_path.open(
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            metadata,
            file,
            indent=4,
            ensure_ascii=False
        )

    return metadata_path


def find_original_file(path):
    original_directory = (
        path / "original"
    )

    if original_directory.is_dir():

        candidates = sorted(
            original_directory.iterdir()
        )

        for candidate in candidates:

            if candidate.is_file():

                return candidate

    preferred_names = (
        "original_selected.jpg",
        "original_selected.jpeg",
        "original.jpg",
        "original.jpeg",
        "original.png",
        "original.bmp",
        "original.webp",
    )

    for filename in preferred_names:

        candidate = path / filename

        if candidate.is_file():

            return candidate

    for candidate in sorted(
        path.iterdir()
    ):

        if not candidate.is_file():
            continue

        name = candidate.name.lower()

        if (
            name.startswith("original")
            and candidate.suffix.lower()
            in {
                ".jpg",
                ".jpeg",
                ".png",
                ".bmp",
                ".webp",
                ".mp4",
                ".avi",
                ".mov",
                ".mkv",
                ".webm",
            }
        ):

            return candidate

    return None


def move_file(
    source,
    destination
):
    destination.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    if destination.exists():

        print(
            "[MIGRATE] Destination already exists - skipped:"
        )

        print(
            f"           {destination}"
        )

        return False

    shutil.move(
        str(source),
        str(destination)
    )

    return True


def reorganize_flat_run(
    source_directory,
    destination_directory
):
    destination_directory.mkdir(
        parents=True,
        exist_ok=False
    )

    original_directory = (
        destination_directory / "original"
    )

    masks_directory = (
        destination_directory / "masks"
    )

    leaves_directory = (
        destination_directory / "leaves"
    )

    overlay_directory = (
        destination_directory / "overlay"
    )

    original_directory.mkdir()
    masks_directory.mkdir()
    leaves_directory.mkdir()
    overlay_directory.mkdir()

    files = list(
        source_directory.iterdir()
    )

    files_moved = 0

    for file in files:

        if not file.is_file():
            continue

        name = file.name.lower()

        if name == "metadata.json":
            continue

        if (
            name.startswith("mask_")
            and file.suffix.lower() == ".png"
        ):

            destination = (
                masks_directory
                / file.name
            )

            if move_file(
                file,
                destination
            ):

                files_moved += 1

            continue

        if (
            name.startswith("leaf_")
            and file.suffix.lower() == ".png"
        ):

            destination = (
                leaves_directory
                / file.name
            )

            if move_file(
                file,
                destination
            ):

                files_moved += 1

            continue

        if name.startswith("overlay"):

            destination = (
                overlay_directory
                / file.name
            )

            if move_file(
                file,
                destination
            ):

                files_moved += 1

            continue

        if name.startswith("original"):

            destination = (
                original_directory
                / file.name
            )

            if move_file(
                file,
                destination
            ):

                files_moved += 1

            continue

    return files_moved


def migrate_flat_directory(
    source_directory,
    destination_root
):
    if not source_directory.is_dir():
        return False

    if is_new_run_structure(
        source_directory
    ):

        return False

    saved_at = get_timestamp(
        source_directory
    )

    original_file = find_original_file(
        source_directory
    )

    if original_file is not None:

        source_file_name = (
            original_file.name
        )

        source_path = str(
            original_file
        )

    else:

        source_file_name = ""

        source_path = ""

    base_name = (
        source_directory.name
    )

    destination = target_directory(
        destination_root,
        base_name,
        saved_at
    )

    print()
    print(
        "============================================================"
    )

    print(
        "[MIGRATE] Old run found:"
    )

    print(
        f"          {source_directory}"
    )

    print(
        "[MIGRATE] New run:"
    )

    print(
        f"          {destination}"
    )

    print(
        "[MIGRATE] Saved date:"
    )

    print(
        f"          {format_display_date(saved_at)}"
    )

    files_moved = reorganize_flat_run(
        source_directory,
        destination
    )

    create_metadata(
        run_directory=destination,
        source_file=source_file_name,
        source_path=source_path,
        saved_at=saved_at,
        original_folder_name=source_directory.name,
        migrated_from=str(
            source_directory
        ),
    )

    print(
        "[MIGRATE] Files moved:"
        f" {files_moved}"
    )

    print(
        "[MIGRATE] metadata.json created."
    )

    try:

        remaining = list(
            source_directory.iterdir()
        )

        if not remaining:

            source_directory.rmdir()

            print(
                "[MIGRATE] Old directory removed."
            )

        else:

            print(
                "[MIGRATE] Old directory was not empty:"
            )

            for item in remaining:

                print(
                    f"           {item}"
                )

    except Exception as error:

        print(
            "[MIGRATE] Could not remove old directory:"
        )

        print(
            f"           {error}"
        )

    return True


def migrate_existing_new_structure(
    run_directory
):
    if not is_new_run_structure(
        run_directory
    ):

        return False

    metadata_path = (
        run_directory
        / "metadata.json"
    )

    if metadata_path.exists():

        print(
            "[MIGRATE] Already migrated:"
            f" {run_directory.name}"
        )

        return False

    saved_at = get_timestamp(
        run_directory
    )

    original_file = find_original_file(
        run_directory
    )

    if original_file is not None:

        source_file = (
            original_file.name
        )

        source_path = str(
            original_file
        )

    else:

        source_file = ""

        source_path = ""

    create_metadata(
        run_directory=run_directory,
        source_file=source_file,
        source_path=source_path,
        saved_at=saved_at,
        original_folder_name=run_directory.name,
        migrated_from=str(
            run_directory
        ),
    )

    print(
        "[MIGRATE] metadata.json added to:"
    )

    print(
        f"          {run_directory}"
    )

    return True


def migrate_old_root():
    if not LEGACY_ROOT.exists():

        print()
        print(
            "[MIGRATE] Legacy directory not found:"
        )

        print(
            f"          {LEGACY_ROOT}"
        )

        return 0

    print()
    print(
        "============================================================"
    )

    print(
        "[MIGRATE] Checking legacy directory:"
    )

    print(
        f"          {LEGACY_ROOT}"
    )

    entries = list(
        LEGACY_ROOT.iterdir()
    )

    files = [
        item
        for item in entries
        if item.is_file()
    ]

    directories = [
        item
        for item in entries
        if item.is_dir()
    ]

    migrated_count = 0

    if files:

        print(
            "[MIGRATE] Legacy root contains direct output files."
        )

        temporary_name = (
            f"legacy_leaf_segmentation_"
            f"{format_timestamp(get_timestamp(LEGACY_ROOT))}"
        )

        destination = target_directory(
            SEGMENTATION_ROOT,
            temporary_name,
            get_timestamp(LEGACY_ROOT)
        )

        SEGMENTATION_ROOT.mkdir(
            parents=True,
            exist_ok=True
        )

        destination.mkdir(
            parents=True,
            exist_ok=False
        )

        for directory_name in (
            "original",
            "masks",
            "leaves",
            "overlay",
        ):

            (
                destination
                / directory_name
            ).mkdir()

        files_moved = 0

        for file in files:

            name = file.name.lower()

            if (
                name.startswith("mask_")
                and file.suffix.lower() == ".png"
            ):

                target = (
                    destination
                    / "masks"
                    / file.name
                )

            elif (
                name.startswith("leaf_")
                and file.suffix.lower() == ".png"
            ):

                target = (
                    destination
                    / "leaves"
                    / file.name
                )

            elif name.startswith("overlay"):

                target = (
                    destination
                    / "overlay"
                    / file.name
                )

            elif name.startswith("original"):

                target = (
                    destination
                    / "original"
                    / file.name
                )

            else:

                print(
                    "[MIGRATE] Unknown legacy file - leaving it:"
                )

                print(
                    f"           {file}"
                )

                continue

            if move_file(
                file,
                target
            ):

                files_moved += 1

        saved_at = get_timestamp(
            LEGACY_ROOT
        )

        original_file = find_original_file(
            destination
        )

        if original_file is not None:

            source_file = (
                original_file.name
            )

        else:

            source_file = ""

        create_metadata(
            run_directory=destination,
            source_file=source_file,
            source_path="",
            saved_at=saved_at,
            original_folder_name="leaf_segmentation",
            migrated_from=str(
                LEGACY_ROOT
            ),
        )

        migrated_count += 1

        print(
            "[MIGRATE] Legacy run converted."
        )

        print(
            f"          {destination}"
        )

        print(
            f"[MIGRATE] Files moved: {files_moved}"
        )

        remaining = list(
            LEGACY_ROOT.iterdir()
        )

        if not remaining:

            try:

                LEGACY_ROOT.rmdir()

                print(
                    "[MIGRATE] Empty legacy directory removed."
                )

            except Exception as error:

                print(
                    "[MIGRATE] Could not remove legacy directory:"
                )

                print(
                    f"           {error}"
                )

    for directory in directories:

        print()
        print(
            "[MIGRATE] Legacy subdirectory:"
        )

        print(
            f"          {directory}"
        )

        if migrate_flat_directory(
            directory,
            SEGMENTATION_ROOT
        ):

            migrated_count += 1

    return migrated_count


def migrate_segmentation_root():
    if not SEGMENTATION_ROOT.exists():

        print(
            "[MIGRATE] Segmentation directory does not exist."
        )

        print(
            f"          {SEGMENTATION_ROOT}"
        )

        return 0

    print()
    print(
        "============================================================"
    )

    print(
        "[MIGRATE] Checking segmentation directory:"
    )

    print(
        f"          {SEGMENTATION_ROOT}"
    )

    migrated_count = 0

    entries = sorted(
        SEGMENTATION_ROOT.iterdir()
    )

    for entry in entries:

        if not entry.is_dir():
            continue

        if entry.name == "performance_history.json":
            continue

        if is_new_run_structure(
            entry
        ):

            if migrate_existing_new_structure(
                entry
            ):

                migrated_count += 1

            continue

        if migrate_flat_directory(
            entry,
            SEGMENTATION_ROOT
        ):

            migrated_count += 1

    return migrated_count


def print_final_summary(
    migrated_count
):
    print()
    print()
    print(
        "============================================================"
    )

    print(
        "PAPRIKA - SEGMENTATION MIGRATION COMPLETED"
    )

    print(
        "============================================================"
    )

    print()

    print(
        f"Runs processed: {migrated_count}"
    )

    print()

    print(
        "Segmentation results are now under:"
    )

    print(
        f"    {SEGMENTATION_ROOT}"
    )

    print()

    print(
        "Expected run structure:"
    )

    print(
        "    <media_name>_YYYYMMDD_HHMMSS"
    )

    print(
        "        original"
    )

    print(
        "        masks"
    )

    print(
        "        leaves"
    )

    print(
        "        overlay"
    )

    print(
        "        metadata.json"
    )

    print()
    print(
        "============================================================"
    )
    print()


def main():
    print()
    print(
        "============================================================"
    )

    print(
        "PAPRIKA - MIGRATE SEGMENTATION RUNS"
    )

    print(
        "============================================================"
    )

    print()

    print(
        "This program reorganizes old segmentation results."
    )

    print(
        "Existing new-format runs are not renamed unnecessarily."
    )

    print()

    try:

        SEGMENTATION_ROOT.mkdir(
            parents=True,
            exist_ok=True
        )

        total_migrated = 0

        total_migrated += (
            migrate_segmentation_root()
        )

        total_migrated += (
            migrate_old_root()
        )

        print_final_summary(
            total_migrated
        )

    except KeyboardInterrupt:

        print()
        print(
            "[MIGRATE] Operation cancelled by user."
        )

        sys.exit(1)

    except Exception as error:

        print()
        print(
            "============================================================"
        )

        print(
            "[MIGRATE] ERROR"
        )

        print(
            "============================================================"
        )

        print(
            f"{type(error).__name__}: {error}"
        )

        print()

        sys.exit(1)


if __name__ == "__main__":
    main()