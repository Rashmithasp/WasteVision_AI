from PIL import Image
from pathlib import Path
import streamlit as st

MODEL_ID = "openai/clip-vit-base-patch32"
CATEGORIES = {
    "plastic": {"name": "Plastic", "prompt": "plastic waste"},
    "paper": {"name": "Paper & cardboard", "prompt": "paper and cardboard waste"},
    "glass": {"name": "Glass", "prompt": "glass waste"},
    "metal": {"name": "Metal", "prompt": "metal waste"},
    "organic": {"name": "Organic", "prompt": "food and organic waste"},
    "electronic": {"name": "Electronic waste", "prompt": "electronic waste"},
    "mixed": {"name": "Mixed / other", "prompt": "mixed household waste"},
}
PROMPT_TO_CATEGORY = {details["prompt"]: key for key, details in CATEGORIES.items()}


@st.cache_resource(show_spinner=False)
def load_model():
    from huggingface_hub import snapshot_download
    from transformers import pipeline

    model_path = snapshot_download(
        repo_id=MODEL_ID,
        local_dir=Path.home() / ".cache" / "wastevision" / "clip-vit-base-patch32",
        allow_patterns=[
            "config.json",
            "pytorch_model.bin",
            "preprocessor_config.json",
            "tokenizer.json",
            "tokenizer_config.json",
            "vocab.json",
            "merges.txt",
            "special_tokens_map.json",
        ],
    )
    return pipeline("zero-shot-image-classification", model=model_path)


def predict(image: Image.Image) -> list[dict[str, str | float]]:
    if not isinstance(image, Image.Image):
        raise TypeError("The classifier expects a Pillow image.")

    results = load_model()(
        image.convert("RGB"),
        candidate_labels=list(PROMPT_TO_CATEGORY),
    )
    predictions = []
    for result in results:
        category = PROMPT_TO_CATEGORY.get(result["label"])
        if category is None:
            continue
        predictions.append(
            {
                "label": category,
                "name": CATEGORIES[category]["name"],
                "score": float(result["score"]),
            }
        )

    if not predictions:
        raise RuntimeError("The model returned no usable category predictions.")
    return predictions
