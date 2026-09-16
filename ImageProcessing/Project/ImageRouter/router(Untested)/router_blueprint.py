# NOTE - the given file is used to decide which AI the image should go through - Sample code for Blueprint (NOT BE USED DIRECTLY)

from pathlib import Path

import torch
import torch.nn.functional as F
from PIL import Image
from transformers import AutoProcessor, AutoModel


MODEL_NAME = "google/medsiglip-448"


CANDIDATES = {
    "rash": "a photograph showing a skin rash",
    "wound": "a photograph showing an open wound",
    "swelling": "a photograph showing visible swelling of a body part",
    "normal": "a photograph showing normal intact skin",
    "other": "a photograph unrelated to a skin or soft-tissue problem",
}


class VisualRouter:

    def __init__(self):

        self.device = (
            "cuda"
            if torch.cuda.is_available()
            else "cpu"
        )

        print(
            f"Loading MedSigLIP on {self.device}..."
        )

        self.processor = AutoProcessor.from_pretrained(
            MODEL_NAME
        )

        self.model = AutoModel.from_pretrained(
            MODEL_NAME,
            device_map="auto",
        )

        self.model.eval()

        self.labels = list(
            CANDIDATES.keys()
        )

        self.texts = list(
            CANDIDATES.values()
        )

        # Pre-compute text representations.
        self.text_features = (
            self._encode_texts()
        )

    def _encode_texts(self):

        inputs = self.processor(
            text=self.texts,
            padding="max_length",
            return_tensors="pt",
        )

        inputs = {
            key: value.to(self.device)
            for key, value in inputs.items()
        }

        with torch.no_grad():

            features = self.model.get_text_features(
                input_ids=inputs["input_ids"],
                attention_mask=inputs["attention_mask"],
            )

        return F.normalize(
            features,
            p=2,
            dim=-1,
        )

    def classify(self, image_path):

        if not Path(image_path).exists():
            raise FileNotFoundError(
                image_path
            )

        image = Image.open(
            image_path
        ).convert("RGB")

        inputs = self.processor(
            images=image,
            return_tensors="pt",
        )

        inputs = {
            key: value.to(self.device)
            for key, value in inputs.items()
        }

        with torch.no_grad():

            image_features = (
                self.model.get_image_features(
                    pixel_values=inputs[
                        "pixel_values"
                    ]
                )
            )

        image_features = F.normalize(
            image_features,
            p=2,
            dim=-1,
        )

        similarities = (
            image_features
            @ self.text_features.T
        )

        scores = similarities[0].tolist()

        ranked = sorted(
            zip(
                self.labels,
                scores,
            ),
            key=lambda x: x[1],
            reverse=True,
        )

        return ranked

