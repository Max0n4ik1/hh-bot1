import os
from sentence_transformers import SentenceTransformer
import torch

# Принудительно используем CPU (чтобы не было проблем с GPU)
os.environ["CUDA_VISIBLE_DEVICES"] = ""
device = torch.device("cpu")

# Загружаем лёгкую модель на CPU
model = SentenceTransformer('all-MiniLM-L6-v2', device="cpu")

def get_embedding(text: str) -> list:
    """
    Превращает текст в вектор чисел (эмбеддинг).
    Работает на процессоре (CPU) — без ошибок с видеокартой.
    """
    if not text:
        return []
    embedding = model.encode(text, normalize_embeddings=True)
    return embedding.tolist()