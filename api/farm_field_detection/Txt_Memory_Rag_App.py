import os
from pathlib import Path
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import streamlit as st
from transformers import AutoTokenizer, AutoModelForCausalLM, TextGenerationPipeline
import torch

# -------------------------- 配置区 --------------------------
DOCS_DIR = "./docs"
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
MODEL_NAME = "gpt2"
CHUNK_SIZE = 800
CHUNK_OVERLAP = 100
GENERATION_KWARGS = dict(max_new_tokens=256, temperature=0.2, top_p=0.95, do_sample=True)
# --------------------------------------------------------

# -------------------------- 文档加载和向量化 --------------------------
docs = []
doc_texts = []
embedder = SentenceTransformer(EMBEDDING_MODEL_NAME)


def chunk_text(text, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap
        if start < 0:
            start = 0
    return chunks


def load_documents(directory=DOCS_DIR):
    global docs, doc_texts, embeddings
    docs.clear()
    doc_texts.clear()
    for p in Path(directory).glob("*.txt"):
        text = p.read_text(encoding="utf-8", errors="ignore")
        chunks = chunk_text(text)
        for c in chunks:
            docs.append({"source": str(p), "content": c})
            doc_texts.append(c)
    embeddings = embedder.encode(doc_texts, convert_to_numpy=True)
    print(f"已加载 {len(doc_texts)} 文本块")


def retrieve_docs_memory(query, top_k=4):
    query_emb = embedder.encode([query], convert_to_numpy=True)
    sims = cosine_similarity(query_emb, embeddings)[0]
    top_indices = np.argsort(-sims)[:top_k]
    return [docs[i] for i in top_indices]


def build_prompt(query, docs_list):
    context = "\n\n".join([f"来源: {d['source']}\n{d['content']}" for d in docs_list])
    prompt = (
        f"下面是从知识库检索到的参考资料（仅作为参考）：\n{context}\n\n"
        f"请基于以上参考资料回答用户问题，并在回答中标注是否完全根据参考资料回答，如无法从参考资料中得出结论请说明并给出合理的推断。\n"
        f"用户问题: {query}\n回答："
    )
    return prompt


class LocalTextGenerator:
    def __init__(self, model_name=MODEL_NAME, device=None):
        self.model_name = model_name
        self.device = device
        self.tokenizer = None
        self.model = None
        self.pipeline = None
        self._init_model()

    def _init_model(self):
        if self.device is None:
            self.device = 0 if torch.cuda.is_available() else -1
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name, use_fast=True)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            device_map="auto"
        )
        self.pipeline = TextGenerationPipeline(model=self.model, tokenizer=self.tokenizer, device=self.device)

    def generate(self, prompt, **kwargs):
        gen_kwargs = GENERATION_KWARGS.copy()
        gen_kwargs.update(kwargs)
        out = self.pipeline(prompt, **gen_kwargs)
        if isinstance(out, list) and len(out) > 0:
            first = out[0]
            return first.get('generated_text') or first.get('text') or str(first)
        return ""


# -------------------------- Streamlit Web UI --------------------------

st.set_page_config(page_title="本地知识库问答（RAG）", layout="wide")
st.title("本地知识库问答（RAG）")

with st.sidebar:
    st.header("运行 & 数据")
    top_k = st.slider("检索 top_k", min_value=1, max_value=10, value=4)
    ingest_path = st.text_input("要导入文档的路径（文件夹）", value=DOCS_DIR)
    if st.button("导入文档"):
        try:
            load_documents(ingest_path)
            st.success("文档加载完成")
        except Exception as e:
            st.error(f"文档加载失败: {e}")

q = st.text_area("提问", height=120)
if st.button("获取答案"):
    if not q.strip():
        st.warning("请先输入问题")
    else:
        with st.spinner("检索相关文档..."):
            try:
                docs_list = retrieve_docs_memory(q, top_k=top_k)
            except Exception as e:
                st.error(f"检索失败: {e}")
                docs_list = []

        st.subheader("检索到的文档")
        for d in docs_list:
            st.markdown(f"**来源:** {d['source']}")
            st.write(d['content'][:1000] + ("..." if len(d['content'])>1000 else ""))

        with st.spinner("生成答案..."):
            try:
                generator = LocalTextGenerator()
                prompt = build_prompt(q, docs_list)
                response = generator.generate(prompt)
            except Exception as e:
                st.error(f"模型生成失败: {e}")
                response = "生成失败"

        st.subheader("模型回答")
        st.write(response)
