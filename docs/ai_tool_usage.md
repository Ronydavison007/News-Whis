# AI Tool Usage Log for NewsWhis

This document captures detailed information on AI model usage, prompts, and tooling logic for each module involved in the NewsWhis financial assistant platform.

---

## 🪤 Voice Input: `voice_agent.py`

### Purpose:

Convert audio queries to text using **OpenAI Whisper**

### Model Used:

* `openai/whisper-base` (default CPU mode)

### Prompt Type:

* Not prompt-based; direct audio transcription

### Notes:

* Transcribes uploaded `.wav` or `.mp3` files
* Used with: `model.transcribe(audio_path)`

---

## 🔗 RAG Retrieval: `rag_agent.py`

### Purpose:

Perform contextual retrieval from scraped documents using FAISS + Sentence Transformers

### Embedding Model:

* `all-MiniLM-L6-v2`
* Provided via: `HuggingFaceEmbeddings(model_name=model_name)`

### Vector DB:

* `FAISS.from_documents()`

### Retrieval Type:

* Top-5 Similarity (cosine)
* Returns source scores & metadata

---

## 📈 Financial Analysis: `analysis_agent.py`

### Purpose:

Analyze AUM trends, regional sentiment, earnings surprises

### AI Use:

* Pure Python logic (no ML models)
* Relies on upstream structured inputs

---

## 🔢 Language Output: `language_agent.py`

### Purpose:

Generate final narrative summary from structured insight data

### Model Used:

* HuggingFace Transformer pipeline via `HuggingFacePipeline`
* Model Example: `tiiuae/falcon-7b-instruct`

### Prompt Structure:

```txt
Generate a financial summary based on the following data:
{earnings_insight}
{aum_change}
{sentiment_summary}
```

### Output:

* Natural language string summary

---

## 🎤 Text-to-Speech: `gtts` usage

### Purpose:

Convert final summary to audio

### Tool:

* `gtts.gTTS(text=narrative, lang='en')`
* Saves to temporary `output_<uuid>.mp3`

---

## 📰 Scraping + News Ingestion: `scrap_agent.py`

### Tools Used:

* `BeautifulSoup` for parsing
* `Selenium + ChromeDriver` for dynamic sites
* `sec-api` for earnings reports

### Prompt Logic:

* Not generative; returns raw HTML text trimmed to relevant tickers

---

## 📊 Market Data API: `api_agent.py`

### Tools:

* `Alpha Vantage` for AUM & prices
* `yfinance` for historical context

---

## 🔹 Parameters & Defaults

| Component     | Key Parameter      | Value                     |
| ------------- | ------------------ | ------------------------- |
| Whisper STT   | `model`            | whisper-base              |
| Embeddings    | `model_name`       | all-MiniLM-L6-v2          |
| RAG Retriever | `top_k`            | 5                         |
| LLM Model     | `model` (pipeline) | falcon-7b-instruct (opt.) |
| TTS           | `lang`             | en                        |

---

## 💡 Optimization Tips

* Use GPU-enabled Whisper + Transformers to reduce latency
* Cache FAISS index for repeated tickers
* Serve Streamlit & FastAPI separately via Docker

---
