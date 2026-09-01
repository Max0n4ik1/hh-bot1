from sentence_transformers import SentenceTransformer
import torch

device = torch.device("cpu")
model = SentenceTransformer('intfloat/multilingual-e5-small', device="cpu")

def get_embedding(text: str) -> list:
    if not text:
        return []
    # Обрезаем текст до 512 токенов (модель поддерживает)
    if len(text) > 2000:
        text = text[:2000]
    embedding = model.encode(text, normalize_embeddings=True)
    return embedding.tolist()