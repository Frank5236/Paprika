from pathlib import Path

import cv2
import numpy as np

from ultralytics import SAM


class LeafSegmenter:

    def __init__(
        self,
        model_path=None
    ):

        self.model_path = (
            Path(model_path)
            if model_path
            else None
        )

        self.model = None

    def load_model(self):

        if self.model_path is None:

            raise ValueError(
                "Leaf segmentation model path was not provided."
            )

        if not self.model_path.exists():

            raise FileNotFoundError(
                "Leaf segmentation model not found:\n"
                f"{self.model_path}"
            )

        print(
            "[LEAF SEGMENTER] "
            f"Loading SAM model: {self.model_path}",
            flush=True
        )

        self.model = SAM(
            str(self.model_path)
        )

        print(
            "[LEAF SEGMENTER] "
            "SAM model loaded successfully.",
            flush=True
        )

    def segment(
        self,
        image_path
    ):

        if self.model is None:

            self.load_model()

        image_path = Path(
            image_path
        )

        if not image_path.exists():

            raise FileNotFoundError(
                "Input image not found:\n"
                f"{image_path}"
            )

        print(
            "[LEAF SEGMENTER] "
            f"Starting segmentation: {image_path}",
            flush=True
        )

        image = cv2.imread(
            str(image_path)
        )

        if image is None:

            raise ValueError(
                "Could not read input image:\n"
                f"{image_path}"
            )

        height, width = image.shape[:2]

        print(
            "[LEAF SEGMENTER] "
            f"Input size: {width} x {height}",
            flush=True
        )

        print(
            "[LEAF SEGMENTER] "
            "Running SAM 2 inference...",
            flush=True
        )

        results = self.model(
            str(image_path),
            verbose=False
        )

        print(
            "[LEAF SEGMENTER] "
            "SAM 2 inference completed.",
            flush=True
        )

        if not results:

            print(
                "[LEAF SEGMENTER] "
                "No results returned.",
                flush=True
            )

            return []

        result = results[0]

        if result.masks is None:

            print(
                "[LEAF SEGMENTER] "
                "No masks found.",
                flush=True
            )

            return []

        masks = (
            result.masks.data
            .cpu()
            .numpy()
        )

        total_masks = len(
            masks
        )

        print(
            "[LEAF SEGMENTER] "
            f"Raw masks detected: {total_masks}",
            flush=True
        )

        leaves = []

        for index, mask in enumerate(
            masks
        ):

            mask = cv2.resize(
                mask,
                (
                    width,
                    height
                ),
                interpolation=cv2.INTER_NEAREST
            )

            mask_binary = (
                mask > 0.5
            ).astype(
                np.uint8
            ) * 255

            ys, xs = np.where(
                mask_binary > 0
            )

            if len(xs) == 0:

                print(
                    "[LEAF SEGMENTER] "
                    f"Mask {index + 1}/{total_masks} "
                    "is empty - skipped.",
                    flush=True
                )

                continue

            x1 = int(
                xs.min()
            )

            y1 = int(
                ys.min()
            )

            x2 = int(
                xs.max()
            )

            y2 = int(
                ys.max()
            )

            area = int(
                np.count_nonzero(
                    mask_binary
                )
            )

            leaf = {
                "id": index + 1,
                "mask": mask_binary,
                "bbox": (
                    x1,
                    y1,
                    x2,
                    y2,
                ),
                "area": area,
                "width": x2 - x1 + 1,
                "height": y2 - y1 + 1,
            }

            leaves.append(
                leaf
            )

            print(
                "[LEAF SEGMENTER] "
                f"Mask {index + 1}/{total_masks} "
                f"area={area} "
                f"bbox=({x1},{y1},{x2},{y2}) "
                f"size={leaf['width']}x{leaf['height']}",
                flush=True
            )

        print(
            "[LEAF SEGMENTER] "
            f"Valid masks returned: {len(leaves)}",
            flush=True
        )

        return leaves