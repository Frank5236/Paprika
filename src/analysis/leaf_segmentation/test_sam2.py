from pathlib import Path
from datetime import datetime
import random
import time

import cv2
import numpy as np
from ultralytics import SAM


IMAGE_PATH = Path(
    r"C:\paprika\images\leafs.jpg"
)

MODEL_PATH = Path(
    r"C:\paprika\images\sam2.1_b.pt"
)

OUTPUT_DIR = Path(
    r"C:\paprika\results\leaf_segmentation"
)


def log(message):

    now = datetime.now().strftime(
        "%H:%M:%S"
    )

    print(
        f"[{now}] {message}",
        flush=True
    )


def main():

    total_start = time.time()

    log("=" * 60)
    log("PAPRIKA - SAM 2 LEAF SEGMENTATION TEST")
    log("=" * 60)

    # --------------------------------------------------
    # STEP 1 - Check image
    # --------------------------------------------------

    log("STEP 1/7 - Checking input image")

    if not IMAGE_PATH.exists():
        raise FileNotFoundError(
            f"Image not found:\n{IMAGE_PATH}"
        )

    log(
        f"Input image: {IMAGE_PATH}"
    )

    image = cv2.imread(
        str(IMAGE_PATH)
    )

    if image is None:
        raise ValueError(
            f"Could not read image:\n{IMAGE_PATH}"
        )

    height, width = image.shape[:2]

    log(
        f"Image loaded: {width} x {height}"
    )

    # --------------------------------------------------
    # STEP 2 - Check model
    # --------------------------------------------------

    log("STEP 2/7 - Checking SAM 2 model")

    if not MODEL_PATH.exists():
        raise FileNotFoundError(
            f"SAM 2 model not found:\n{MODEL_PATH}"
        )

    model_size_mb = (
        MODEL_PATH.stat().st_size
        / (1024 * 1024)
    )

    log(
        f"Model found: {MODEL_PATH}"
    )

    log(
        f"Model size: {model_size_mb:.2f} MB"
    )

    # --------------------------------------------------
    # STEP 3 - Prepare output
    # --------------------------------------------------

    log("STEP 3/7 - Preparing output directory")

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    log(
        f"Output directory: {OUTPUT_DIR}"
    )

    # --------------------------------------------------
    # STEP 4 - Load model
    # --------------------------------------------------

    log("STEP 4/7 - Loading SAM 2 model")
    log("Please wait - model loading can take some time...")

    model_start = time.time()

    model = SAM(
        str(MODEL_PATH)
    )

    model_elapsed = (
        time.time() - model_start
    )

    log(
        f"SAM 2 model loaded successfully "
        f"({model_elapsed:.2f} sec)"
    )

    # --------------------------------------------------
    # STEP 5 - Run inference
    # --------------------------------------------------

    log("STEP 5/7 - Running SAM 2 segmentation")
    log("Please wait - inference is now running...")

    inference_start = time.time()

    results = model(
        str(IMAGE_PATH),
        verbose=False
    )

    inference_elapsed = (
        time.time() - inference_start
    )

    log(
        f"Inference completed "
        f"({inference_elapsed:.2f} sec)"
    )

    if not results:
        log("ERROR - No results returned")
        return

    result = results[0]

    if result.masks is None:
        log("ERROR - No masks found")
        return

    masks = (
        result.masks.data
        .cpu()
        .numpy()
    )

    mask_count = len(masks)

    log(
        f"Total masks detected: {mask_count}"
    )

    # --------------------------------------------------
    # STEP 6 - Save masks
    # --------------------------------------------------

    log("STEP 6/7 - Saving masks and creating overlay")

    overlay = image.copy()

    random.seed(42)

    mask_start = time.time()

    for index, mask in enumerate(masks):

        mask_number = index + 1

        log(
            f"Processing mask "
            f"{mask_number}/{mask_count}"
        )

        mask = cv2.resize(
            mask,
            (width, height),
            interpolation=cv2.INTER_NEAREST
        )

        mask_binary = (
            mask > 0.5
        ).astype(np.uint8)

        color = np.array(
            [
                random.randint(50, 255),
                random.randint(50, 255),
                random.randint(50, 255),
            ],
            dtype=np.uint8
        )

        colored_mask = np.zeros_like(
            image
        )

        colored_mask[
            mask_binary > 0
        ] = color

        overlay = cv2.addWeighted(
            overlay,
            0.65,
            colored_mask,
            0.35,
            0
        )

        mask_file = (
            OUTPUT_DIR
            / f"mask_{mask_number:03d}.png"
        )

        cv2.imwrite(
            str(mask_file),
            mask_binary * 255
        )

        log(
            f"Saved: {mask_file.name}"
        )

    mask_elapsed = (
        time.time() - mask_start
    )

    log(
        f"All {mask_count} masks saved "
        f"({mask_elapsed:.2f} sec)"
    )

    # --------------------------------------------------
    # STEP 7 - Save final images
    # --------------------------------------------------

    log("STEP 7/7 - Saving final images")

    original_file = (
        OUTPUT_DIR
        / "original.jpg"
    )

    overlay_file = (
        OUTPUT_DIR
        / "overlay.jpg"
    )

    cv2.imwrite(
        str(original_file),
        image
    )

    log(
        f"Saved original: {original_file}"
    )

    cv2.imwrite(
        str(overlay_file),
        overlay
    )

    log(
        f"Saved overlay: {overlay_file}"
    )

    total_elapsed = (
        time.time() - total_start
    )

    log("=" * 60)
    log("TEST COMPLETED SUCCESSFULLY")
    log(
        f"Total processing time: "
        f"{total_elapsed:.2f} sec"
    )
    log(
        f"Masks created: {mask_count}"
    )
    log(
        f"Results directory: {OUTPUT_DIR}"
    )
    log("=" * 60)


if __name__ == "__main__":
    main()