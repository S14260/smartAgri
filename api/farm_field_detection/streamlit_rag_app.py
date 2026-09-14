"""
Streamlit RAG: 本地知识库问答系统（TXT 内存版 + session_state + 模型只加载一次）
"""

import os
import sys
from pathlib import Path
from typing import List

import streamlit as st
import numpy as np
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForCausalLM, TextGenerationPipeline
from sklearn.metrics.pairwise import cosine_similarity

# -------------------------- 配置区 --------------------------
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
MODEL_NAME = os.environ.get("RAG_MODEL_NAME", "gpt2")  # 可替换为本地更强模型
GENERATION_KWARGS = dict(max_new_tokens=256, temperature=0.2, top_p=0.95, do_sample=True)
CHUNK_SIZE = 800
CHUNK_OVERLAP = 100

# -------------------------- 工具函数 --------------------------
def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    if not text:
        return []
    if len(text) <= chunk_size:
        return [text]
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - overlap
        if start < 0:
            start = 0
    return chunks

# -------------------------- 文本生成器 --------------------------
class LocalTextGenerator:
    _instance = None  # 单例模式，避免重复加载模型

    def __new__(cls, model_name: str = MODEL_NAME):
        if cls._instance is None:
            cls._instance = super(LocalTextGenerator, cls).__new__(cls)
            cls._instance._init_model(model_name)
        return cls._instance

    def _init_model(self, model_name: str):
        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name, use_fast=True)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype=None,
            device_map=None  # 不使用 device_map 避免 accelerate 错误
        )
        self.pipeline = TextGenerationPipeline(model=self.model, tokenizer=self.tokenizer)

    def generate(self, prompt: str, **kwargs) -> str:
        gen_kwargs = GENERATION_KWARGS.copy()
        gen_kwargs.update(kwargs)
        out = self.pipeline(prompt, **gen_kwargs)
        if isinstance(out, list) and len(out) > 0:
            first = out[0]
            return first.get('generated_text') or first.get('text') or str(first)
        return ""

# -------------------------- Streamlit App --------------------------
st.set_page_config(page_title="本地知识库问答（RAG）", layout="wide")
st.title("本地知识库问答（RAG）")

# session_state 初始化
if 'docs' not in st.session_state:
    st.session_state.docs = []
if 'doc_texts' not in st.session_state:
    st.session_state.doc_texts = []
if 'embeddings' not in st.session_state:
    st.session_state.embeddings = None
if 'generator' not in st.session_state:
    st.session_state.generator = None

# Embedding 模型初始化
embedder = SentenceTransformer(EMBEDDING_MODEL_NAME)

# -------------------------- 侧边栏 --------------------------
with st.sidebar:
    st.header("运行 & 数据")
    model_name = st.text_input("文本生成模型（HuggingFace 名称或本地路径）", value=MODEL_NAME)
    top_k = st.slider("检索 top_k", min_value=1, max_value=10, value=4)
    ingest_path = st.text_input("要导入文档的路径（文件夹）", value="./docs")

    def import_docs(path):
        docs = []
        doc_texts = []
        for f in Path(path).glob("*.txt"):
            text = f.read_text(encoding="utf-8", errors="ignore")
            chunks = chunk_text(text)
            for i, c in enumerate(chunks):
                docs.append({"source": str(f), "content": c, "chunk": i})
                doc_texts.append(c)
        if doc_texts:
            embeddings = embedder.encode(doc_texts, convert_to_numpy=True)
            st.session_state.docs = docs
            st.session_state.doc_texts = doc_texts
            st.session_state.embeddings = embeddings
            st.success(f"已加载 {len(doc_texts)} 文本块")
        else:
            st.warning("没有找到有效文档")

    if st.button("导入文档"):
        import_docs(ingest_path)

# -------------------------- 主界面 --------------------------
q = st.text_area("提问（输入后点击‘获取答案’）", height=120)

def retrieve_docs_session(query, top_k=4):
    # 判断是否已经有 embeddings
    if st.session_state.embeddings is None or len(st.session_state.doc_texts) == 0:
        return []
    query_emb = embedder.encode([query], convert_to_numpy=True)
    sims = cosine_similarity(query_emb, st.session_state.embeddings)[0]
    top_indices = np.argsort(sims)[::-1][:top_k]
    return [st.session_state.docs[i] for i in top_indices]

def build_prompt(query: str, docs: List[dict]) -> str:
    context = "\n\n".join([f"来源: {d['source']}\n{d['content']}" for d in docs])
    prompt = (
        "下面是从知识库检索到的参考资料（仅作为参考）：\n"
        f"{context}\n\n"
        "请基于以上参考资料回答用户问题，并在回答中标注是否完全根据参考资料回答，如无法从参考资料中得出结论请说明并给出合理的推断。\n"
        f"用户问题: {query}\n"
        "回答："
    )
    return prompt

colA, colB = st.columns([3,1])
if colB.button("获取答案"):
    if not q.strip():
        st.warning("请先输入问题。")
    else:
        docs_list = retrieve_docs_session(q, top_k)
        if docs_list:
            st.subheader("检索到的文档（按相关性）")
            for d in docs_list:
                st.markdown(f"**来源:** {d['source']} &nbsp;&nbsp;|&nbsp;&nbsp;chunk: {d['chunk']}")
                st.write(d['content'][:1000] + ("..." if len(d['content']) > 1000 else ""))

            with st.spinner("生成答案..."):
                if st.session_state.generator is None:
                    st.session_state.generator = LocalTextGenerator(model_name=model_name)
                prompt = build_prompt(q, docs_list)
                response = st.session_state.generator.generate(prompt)
            st.subheader("模型回答")
            st.write(response)
        else:
            st.warning("当前没有可检索的文档，请先导入文档")
