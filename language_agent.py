from langchain_huggingface import HuggingFacePipeline
from langchain.schema import Document
from transformers import pipeline
from typing import List, Tuple, Dict
import re
import numpy as np


def preprocess_retrieved(retrieved: List[Document], maxlen: int = 1000) -> str:
    context = ''
    for doc in retrieved:
        ticker = doc.metadata.get('ticker', 'unknown')
        content = doc.page_content
        context += f'Ticker: {ticker}\nContent: {content}\n\n'
    return context[:maxlen]


def check_relevance(retrieved: List[Document], threshold: float = 0.7) -> Tuple[bool, str]:
    for doc in retrieved:
        score = doc.metadata.get('score', 0)
        if score < threshold:
            return False, 'Could you clarify your query? The retrieved information is insufficient.'
    return True, None


def extract_earnings_summary(retrieved_docs: List[Document]) -> str:
    summary = []
    for doc in retrieved_docs:
        ticker = doc.metadata.get('ticker', 'unknown')
        content = doc.page_content.lower()

        match = re.search(r'(beat|missed) estimates by ([\d.]+)%', content)
        if match:
            action, percent = match.groups()
            summary.append(f"{ticker.upper()} {action} estimates by {percent}%")

    return '\n'.join(summary)


def generate_narrative(query: str, retrieved_docs: List[Document], analysis_data: Dict[str, any]) -> Tuple[str, List[dict]]:
    is_conf, clarity = check_relevance(retrieved_docs)
    if not is_conf:
        return clarity, []

    context = preprocess_retrieved(retrieved_docs)
    earnings_summary = extract_earnings_summary(retrieved_docs)
    portfolio = analysis_data.get('portfolio', {
        'allocation': 22.0,
        'change': 'up from 18% yesterday',
        'sentiment': 'Neutral'
    })

    # Build clean natural language prompt
    prompt = f"""
You are a finance assistant delivering a morning market brief.

Respond in this exact format:
"Today, your American tech allocation is {portfolio['allocation']}% of AUM, {portfolio['change']}.
{earnings_summary if earnings_summary else 'No earnings surprises found.'}
Regional sentiment is {portfolio['sentiment']}."
"""

    pipe = pipeline("text2text-generation", model="google/flan-t5-small", max_new_tokens=500)
    llm = HuggingFacePipeline(pipeline=pipe)
    response = llm.invoke(prompt)  # invoke instead of __call__

    # Clean up metadata to avoid serialization errors
    sources = [
        {k: float(v) if isinstance(v, np.floating) else v for k, v in doc.metadata.items()}
        for doc in retrieved_docs
    ]

    return response, sources
