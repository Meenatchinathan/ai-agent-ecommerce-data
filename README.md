# 🛍️ E-commerce AI Agent

This project implements an **AI agent** that answers natural language questions about e-commerce data by converting them to SQL queries. The system uses a **local LLM (Mistral-7B)** for query generation and provides both **API** and **CLI** interfaces.

![Demo](https://via.placeholder.com/800x400.png?text=E-commerce+AI+Agent+Demo)

## ✨ Features

- 🧠 Natural language to SQL conversion  
- 💾 Local LLM execution (no internet required)  
- 📊 Data visualization support  
- ⚡ Streamed responses (typing effect)  
- 📦 Self-contained SQLite database  

## 🧰 Prerequisites

- Python 3.8+  
- 8GB+ RAM (16GB recommended)  
- 5GB+ disk space  

## 🚀 Installation

1. Clone Repository:  
`git clone https://github.com/yourusername/ecommerce-ai-agent.git`  
`cd ecommerce-ai-agent`

2. Create Virtual Environment:  
`python -m venv venv`  
`source venv/bin/activate` (for Linux/macOS)  
`venv\Scripts\activate` (for Windows)

3. Install Dependencies:  
`pip install -r requirements.txt`

4. Download LLM Model:  
`mkdir -p models`  
`wget -O models/mistral-7b-openorca.Q4_K_M.gguf https://huggingface.co/TheBloke/Mistral-7B-OpenOrca-GGUF/resolve/main/mistral-7b-openorca.Q4_K_M.gguf`  
📁 File size: ~4.37GB

5. Load Data:  
`python data_loader/load_data.py`

## 🧪 Usage

Start the API server:  
`uvicorn app.main:app --reload`  
API will be available at: http://localhost:8000

Ask questions via API:  
`curl -X POST "http://localhost:8000/query" -H "Content-Type: application/json" -d '{"question":"What is total sales?"}'`

Run demo script:  
`python scripts/demo_questions.py`

Interactive API docs available at:  
http://localhost:8000/docs

## 📁 Project Structure

ecommerce-ai-agent/  
├── app/                   # FastAPI application  
│   ├── main.py            # API endpoints  
│   ├── llm_helper.py      # LLM integration  
│   ├── visualization.py   # Plot generation  
│   └── schemas.py         # Data models  
├── data_loader/           # Data ingestion  
│   └── load_data.py       # Google Sheets to SQLite  
├── database/              # SQLite database  
│   └── ecommerce.db  
├── models/                # LLM models (not in repo)  
│   └── mistral-7b-openorca.Q4_K_M.gguf  
├── scripts/               # Demo scripts  
│   ├── demo_questions.py  # Python demo  
│   └── demo_api.sh        # cURL demo  
├── requirements.txt       # Python dependencies  
└── README.md              # This file  

## ❓ Demo Questions

1. What is my total sales?  
`SELECT SUM(total_sales) FROM total_sales_metrics;`

2. Calculate the RoAS (Return on Ad Spend)  
`SELECT SUM(ad_sales)/SUM(ad_spend) AS roas FROM ad_sales_metrics;`

3. Which product had the highest CPC (Cost Per Click)?  
`SELECT product_id, MAX(cost_per_click) FROM ad_sales_metrics GROUP BY product_id ORDER BY MAX(cost_per_click) DESC LIMIT 1;`

## ⚙️ Configuration

Edit the `.env` file:

PORT=8000  
HOST=0.0.0.0  
MODEL_PATH=models/mistral-7b-openorca.Q4_K_M.gguf  
LLM_THREADS=8  
LLM_GPU_LAYERS=1  # Set to 0 for CPU-only

## 🛠️ Troubleshooting

- Model not found: Ensure the file exists at `models/mistral-7b-openorca.Q4_K_M.gguf`
- SSL errors: Run `pip install certifi --upgrade`
- Memory issues: Lower `LLM_THREADS` in `.env`
- For M1/M2 Mac users:  
Run `CMAKE_ARGS="-DLLAMA_METAL=on" pip install --force-reinstall llama-cpp-python`

