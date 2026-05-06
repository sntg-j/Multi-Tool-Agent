from custom_tools import function_name_getter
from langchain_milvus import Milvus
from langchain_core.embeddings import Embeddings
from sentence_transformers import SentenceTransformer, InputExample, losses
from torch.utils.data import DataLoader

# Load a base model to fine-tune
model = SentenceTransformer("all-MiniLM-L6-v2")

# Your training data — pairs of (text, similar_text)
# train_examples = [
#     InputExample(texts=["vector database", "embedding storage"]),
#     InputExample(texts=["machine learning", "neural networks"]),
#     InputExample(texts=["your domain term", "related domain term"]),
# ]
train_examples = [InputExample(texts=i) for i in function_name_getter()]

train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=16)

# MultipleNegativesRankingLoss is best for semantic similarity
loss = losses.MultipleNegativesRankingLoss(model)

model.fit(
    train_objectives=[(train_dataloader, loss)],
    epochs=3,
    warmup_steps=100,
    output_path="./my-finetuned-model"
)

class SentenceTransformerEmbeddings(Embeddings):
    def __init__(self, model_path: str):
        self.model = SentenceTransformer(model_path)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return self.model.encode(texts, normalize_embeddings=True).tolist()

    def embed_query(self, text: str) -> list[float]:
        return self.model.encode([text], normalize_embeddings=True)[0].tolist()

# ── 3. Set up Milvus with local .db file (replaces :memory:) ─────────────────
embeddings = SentenceTransformerEmbeddings("./my-finetuned-model")

vectorstore = Milvus(
    embedding_function=embeddings,          # pass the object, not raw vectors
    connection_args={"uri": "./milvus_local.db"},  # .db file instead of :memory:
)

texts = function_name_getter()  # your list of texts
# for text in texts:
vectorstore.add_texts(["hello","worlds"])

results = vectorstore.similarity_search("fast vector DB", k=2)
print(results)