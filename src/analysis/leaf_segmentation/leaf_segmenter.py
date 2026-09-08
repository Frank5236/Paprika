from pathlib import Path

import cv2
import numpy as np

from ultralytics import SAM


class LeafSegmenter:

    def __init__(self, model_path=None):
        self.model_path = Path(model_path) if model_path else None
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

        self.model = SAM(str(self.model_path))

        print(
            "[LEAF SEGMENTER] SAM model loaded successfully.",
            flush=True
        )

    def clean_mask(self, mask_binary):
        kernel = np.ones((3, 3), np.uint8)
        cleaned = cv2.morphologyEx(
            mask_binary,
            cv2.MORPH_OPEN,
            kernel,
            iterations=1
        )
        cleaned = cv2.morphologyEx(
            cleaned,
            cv2.MORPH_CLOSE,
            kernel,
            iterations=1
        )
        return cleaned

    def mask_iou(self, mask_a, mask_b):
        a = mask_a > 0
        b = mask_b > 0

        intersection = np.count_nonzero(a & b)
        union = np.count_nonzero(a | b)

        if union == 0:
            return 0.0

        return intersection / union

    def segment(self, image_path):
        if self.model is None:
            self.load_model()

        image_path = Path(image_path)

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

        image = cv2.imread(str(image_path))

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
            "[LEAF SEGMENTER] Running SAM 2 inference...",
            flush=True
        )

        results = self.model(
            str(image_path),
            verbose=False
        )

        print(
            "[LEAF SEGMENTER] SAM 2 inference completed.",
            flush=True
        )

        if not results:
            print(
                "[LEAF SEGMENTER] No results returned.",
                flush=True
            )
            return []

        result = results[0]

        if result.masks is None:
            print(
                "[LEAF SEGMENTER] No masks found.",
                flush=True
            )
            return []

        masks = result.masks.data.cpu().numpy()

        total_masks = len(masks)

        print(
            "[LEAF SEGMENTER] "
            f"Raw masks detected: {total_masks}",
            flush=True
        )

        min_area = max(
            20,
            int(width * height * 0.001)
        )

        max_area = int(width * height * 0.95)

        print(
            "[LEAF SEGMENTER] "
            f"Minimum mask area: {min_area}",
            flush=True
        )

        print(
            "[LEAF SEGMENTER] "
            f"Maximum mask area: {max_area}",
            flush=True
        )

        candidates = []

        for index, mask in enumerate(masks):
            mask = cv2.resize(
                mask,
                (width, height),
                interpolation=cv2.INTER_NEAREST
            )

            mask_binary = (
                mask > 0.5
            ).astype(np.uint8) * 255

            mask_binary = self.clean_mask(mask_binary)

            area = int(np.count_nonzero(mask_binary))

            if area < min_area:
                print(
                    "[LEAF SEGMENTER] "
                    f"Mask {index + 1}/{total_masks} rejected: "
                    f"area {area} < {min_area}",
                    flush=True
                )
                continue

            if area > max_area:
                print(
                    "[LEAF SEGMENTER] "
                    f"Mask {index + 1}/{total_masks} rejected: "
                    f"area {area} > {max_area}",
                    flush=True
                )
                continue

            ys, xs = np.where(mask_binary > 0)

            if len(xs) == 0:
                print(
                    "[LEAF SEGMENTER] "
                    f"Mask {index + 1}/{total_masks} rejected: empty",
                    flush=True
                )
                continue

            x1 = int(xs.min())
            y1 = int(ys.min())
            x2 = int(xs.max())
            y2 = int(ys.max())

            candidates.append({
                "source_index": index,
                "mask": mask_binary,
                "bbox": (x1, y1, x2, y2),
                "area": area,
                "width": x2 - x1 + 1,
                "height": y2 - y1 + 1,
            })

        candidates.sort(
            key=lambda item: item["area"],
            reverse=True
        )

        filtered = []
        duplicate_iou = 0.85

        for candidate in candidates:
            duplicate = False

            for accepted in filtered:
                iou = self.mask_iou(
                    candidate["mask"],
                    accepted["mask"]
                )

                if iou >= duplicate_iou:
                    duplicate = True
                    print(
                        "[LEAF SEGMENTER] "
                        f"Mask source {candidate['source_index'] + 1} "
                        f"rejected: duplicate IoU={iou:.3f}",
                        flush=True
                    )
                    break

            if not duplicate:
                filtered.append(candidate)

        leaves = []

        for leaf_number, candidate in enumerate(filtered, start=1):
            x1, y1, x2, y2 = candidate["bbox"]

            leaf = {
                "id": leaf_number,
                "source_index": candidate["source_index"] + 1,
                "mask": candidate["mask"],
                "bbox": candidate["bbox"],
                "area": candidate["area"],
                "width": candidate["width"],
                "height": candidate["height"],
                "center_x": (x1 + x2) / 2.0,
                "center_y": (y1 + y2) / 2.0,
            }

            leaves.append(leaf)

            print(
                "[LEAF SEGMENTER] "
                f"Leaf {leaf_number}: "
                f"area={leaf['area']} "
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


if __name__ == "__main__":
    image_path = Path(
        r"C:\paprika\images\leafs.jpg"
    )

    segmenter = LeafSegmenter(
        r"C:\paprika\images\sam2.1_b.pt"
    )

    leaves = segmenter.segment(image_path)

    print(
        f"LEAVES DETECTED: {len(leaves)}",
        flush=True
    )
