"""
Example script for running inference with the `jina‑clip‑v2` model using
Hugging Face Transformers on a CUDA‐enabled Linux system.

The script demonstrates how to load the pre‑trained model, process text and image
inputs, and obtain multimodal embedding vectors suitable for similarity search.
It uses the `AutoModel` API with `trust_remote_code=True` to pull in the custom
implementation provided by Jina AI.  Images are read with PIL and resized
internally by the model’s processor (no manual resizing is required).  The
Matryoshka representation allows you to reduce the embedding dimension by
setting ``truncate_dim``—for example to 512 or 256—without retraining【467972863972710†L241-L247】.

Prerequisites
-------------
- Create and activate the conda environment defined in ``jina_clip_v2_env.yml``.
  This environment installs PyTorch with CUDA support, Transformers, timm,
  pillow, and optional packages such as ``flash‑attn`` and ``xformers`` for
  faster attention on GPUs【467972863972710†L284-L289】.  Use ``conda env create -f
  jina_clip_v2_env.yml`` and ``conda activate jina‑clip‑v2‑inference``.

- The first time you run this script, the model weights (~15 GB) and
  associated configuration will be downloaded from the Hugging Face hub.  If
  internet access is restricted, download the files manually and point the
  ``cache_dir`` argument in ``from_pretrained`` to the local directory.

Usage
-----
Run the script directly to see example embeddings and cosine similarities::

    python jina_clip_v2_inference_example.py

"""

import os
from typing import List, Union

import torch
from PIL import Image
from transformers import AutoModel


def load_jina_clip_model(model_name: str = "jinaai/jina-clip-v2",
                         device: Union[str, torch.device] = None,
                         cache_dir: str = None):
    """Load the Jina CLIP v2 model for inference.

    Parameters
    ----------
    model_name : str
        Identifier of the model on Hugging Face hub (default
        ``"jinaai/jina-clip-v2"``).
    device : str or torch.device, optional
        Device to place the model on (e.g., ``"cuda"`` or ``"cpu"``).  If
        ``None``, uses CUDA when available.  The model exposes its own
        ``encode_text`` and ``encode_image`` methods.
    cache_dir : str, optional
        Directory to cache the downloaded model.  Use this when running
        offline.

    Returns
    -------
    model : transformers.PreTrainedModel
        The loaded model ready for encoding text and images.
    device : torch.device
        The resolved device on which the model is placed.
    """
    resolved_device = torch.device(
        device if device is not None else ("cuda" if torch.cuda.is_available() else "cpu")
    )
    # Load the model with trust_remote_code=True to use Jina’s custom encoder implementation【467972863972710†L344-L380】.
    model = AutoModel.from_pretrained(
        model_name,
        trust_remote_code=True,
        torch_dtype=torch.bfloat16 if resolved_device.type == "cuda" else None,
        cache_dir=cache_dir,
    )
    # Move model to the desired device
    model.to(resolved_device)
    # Switch model to evaluation mode for inference
    model.eval()
    return model, resolved_device


def embed_text(model, texts: Union[str, List[str]], truncate_dim: int = 512) -> torch.Tensor:
    """Encode one or more text strings into embeddings.

    Parameters
    ----------
    model : transformers.PreTrainedModel
        The Jina CLIP v2 model loaded via ``load_jina_clip_model``.
    texts : str or list of str
        Text or list of texts to encode.  Can be multilingual; the model
        supports 89 languages【467972863972710†L237-L239】.
    truncate_dim : int
        Dimension of the returned embeddings.  Set to ``None`` to use the full
        1024‑dimensional Matryoshka representation【467972863972710†L245-L247】.

    Returns
    -------
    embeddings : torch.Tensor
        A tensor of shape ``(n, truncate_dim)`` containing L2‑normalized
        embeddings.  When encoding a single string, returns a tensor of shape
        ``(1, truncate_dim)``.
    """
    # The model’s encode_text method accepts both strings and list of strings【467972863972710†L344-L380】.
    return model.encode_text(texts, truncate_dim=truncate_dim)


def embed_images(model, images: List[Union[str, Image.Image]], truncate_dim: int = 512) -> torch.Tensor:
    """Encode a batch of images into embeddings.

    Parameters
    ----------
    model : transformers.PreTrainedModel
        The Jina CLIP v2 model loaded via ``load_jina_clip_model``.
    images : list
        A list containing either ``PIL.Image.Image`` objects, file paths to
        local images, or URLs.  The model internally resizes images to
        512×512 pixels as required【467972863972710†L241-L244】.
    truncate_dim : int
        Dimension of the returned embeddings.  Set to ``None`` for the full
        1024 dimensions【467972863972710†L245-L247】.

    Returns
    -------
    embeddings : torch.Tensor
        A tensor of shape ``(n, truncate_dim)`` containing L2‑normalized
        embeddings for each image.
    """
    # encode_image accepts PIL images, file names, URLs or data URIs【467972863972710†L344-L380】.
    return model.encode_image(images, truncate_dim=truncate_dim)


def cosine_similarity(a: torch.Tensor, b: torch.Tensor) -> float:
    """Compute the cosine similarity between two vectors."""
    a_norm = a / a.norm(dim=-1, keepdim=True)
    b_norm = b / b.norm(dim=-1, keepdim=True)
    return float((a_norm * b_norm).sum())


if __name__ == "__main__":
    # Load the model on the most appropriate device (GPU if available)
    model, device = load_jina_clip_model()

    # Example texts in different languages (Arabic, Chinese, English)
    texts = [
        "غروب جميل على الشاطئ",  # Arabic
        "海滩上美丽的日落",        # Chinese
        "A beautiful sunset over the beach",  # English
    ]

    # Encode the texts
    text_embeds = embed_text(model, texts, truncate_dim=512)
    print(f"Encoded {len(texts)} texts to shape {text_embeds.shape}")

    # Load a local image using PIL (replace with your own image path)
    image_path = os.path.join(os.path.dirname(__file__), "example.jpg")
    if os.path.exists(image_path):
        pil_image = Image.open(image_path).convert("RGB")
        # Encode the image (note: a list is required even for a single image)
        image_embeds = embed_images(model, [pil_image], truncate_dim=512)
        print(f"Encoded 1 image to shape {image_embeds.shape}")

        # Compute and display cosine similarity between the English text and the image
        english_idx = 2  # index of the English sentence
        score = cosine_similarity(text_embeds[english_idx], image_embeds[0])
        print(f"Cosine similarity (text vs. image): {score:.4f}")
    else:
        print(
            "Example image not found. To test image encoding, place an image named"
            " 'example.jpg' in the same directory as this script."
        )
