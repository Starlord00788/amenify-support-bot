# Amenify Summer 2026 – Software Engineering Internship Assignment

🌟 **Live Demo:** [https://starlord00788.github.io/amenify-support-bot/](https://starlord00788.github.io/amenify-support-bot/)

Hello! This project implements a fully functional, lightweight AI customer support bot exclusively answering questions based on the content of amenify.com.

**Important Note regarding "absolutely free" tier requirement:**
1. **Embeddings/Vector Search**: Designed to be 100% free by using `scikit-learn`'s `TfidfVectorizer` and `cosine_similarity`. It runs locally and costs nothing, avoiding any need to pay for embedding APIs like `text-embedding-ada-002` or `cohere`.
2. **Generative API**: The configuration file supports standard `OPENAI_API_KEY`. To ensure completely free, high-speed usage, the backend is configured to use Groq's OpenAI-compatible API running the `llama-3.3-70b-versatile` model. 

## 🚀 Live Deployment
- **Frontend:** Hosted statically on GitHub Pages.
- **Backend API:** Hosted on Render.com (FastAPI).

---

## Local Setup Instructions

1. **Clone and Enter Directory**
   ```bash
   cd amenify-support-bot
   ```

2. **Setup Environment**
   ```bash
   python -m venv venv
   # On Windows:
   venv\\Scripts\\activate
   # On Mac/Linux:
   source venv/bin/activate
   
   pip install -r requirements.txt
   ```

3. **Configure API Keys**
   - Copy `.env.example` to a new file named `.env`.
   - Update `OPENAI_API_KEY` inside `.env` with a real key!

4. **Prepare the Knowledge Base**
   Run the simple scraper script to pull data from Amenify.
   ```bash
   python scraper.py
   ```
   *This outputs `data/knowledge_base.txt`.*

5. **Start the API Backend**
   ```bash
   python main.py
   ```

6. **Open the Chat Interface**
   Open `index.html` in your web browser (e.g. Chrome). No complex build steps needed.
   Double click the file or serve it:
   ```bash
   npx http-server . # (optional)
   ```

## Example Queries
- Q: "What services does Amenify offer?" -> A: "Amenify provides..."
- Q: "Who built Amenify?" -> A: "I don't know." (Since it may not be on the main page)
- Q: "What is the capital of France?" -> A: "I don't know."


---

## Section 3: Reasoning & Design
**Answers Filled In:**

### 1. How did you ingest and structure the data from the website?
I used `beautifulsoup4` combined with `requests` to crawl the homepage headers and paragraph tags. To clean and structure the data, I filtered out extremely short strings (under 20 characters) avoiding navigation noise, deduplicated the lines while preserving layout order, and saved it linearly to `data/knowledge_base.txt`. 

### 2. How did you reduce hallucinations?
To eliminate hallucinations, I used a multi-layered approach:
1. Retrieval constraint: I retrieve the top chunks that match using TF-IDF locally and pass ONLY those chunks instead of huge documents.
2. System Prompts: The system message rigidly instructs the LLM: *“You must ONLY answer incoming questions using the exact information provided in the Context below. If the answer cannot be found in the Context provided below, you MUST respond with precisely: "I don't know".”*
3. Temperature constraint: `temperature=0.0` strongly reduces creative interpolation in the output payload.

### 3. What are the limitations of your approach?
1. The currently naive web scraper mainly scrapes only the landing page `https://amenify.com/`. Deeply nested pages (like FAQs on subpages) require recursive scraping.
2. TF-IDF vector space modeling performs well for verbatim word overlap but struggles with deeper semantic nuances compared to modern dense embedding models (like transformer embeddings).
3. The chatbot does not stream token responses to the UI currently, which can make users feel like the bot is unresponsive during higher latency queries.

### 4. How would you scale this system?
1. Replace local flat-file extraction with a periodic Crawler/CronJob dropping structured data into a managed robust database (e.g., PostgreSQL or MongoDB).
2. Move from local TF-IDF matrices to a proper scalable Vector Database like Pinecone, Qdrant, or PgVector.
3. Decouple ML Inference workers queueing from the REST API to handle sudden API spikes without locking up FastAPI's concurrency limits.

### 5. What improvements would you make for production use?
1. Implement a conversation database cache (e.g., Redis) to track ongoing sessions strictly and scale stateless endpoints across many node clusters.
2. Add rate limiting on the API layer (`fastapi-limiter`) to prevent brute force scraping or API-abuse leading to massive OpenAI bills. 
3. Instrument observability (Prometheus / Datadog) to track things like "Time to first token", "Cosine threshold misses", and "API 500 crashes".
4. Upgrade to dense embedding models (`text-embedding-3-small`) paired with chunking algorithms like Semantic Chunking instead of pure line-by-line TF-IDF. 

---
**Applicant:** Palash
**LinkedIn:** [(https://www.linkedin.com/in/palash-singhal-299134293/)]
