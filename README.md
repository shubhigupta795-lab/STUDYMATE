# STUDYMATE V1

STUDYMATE V1 is the source-ingestion layer of the research workspace.

It takes one of three inputs:

- DOCX research paper
- PDF research paper
- raw YouTube transcript text

The system extracts research-focused structured knowledge with Gemini, including:

- research problem and objective
- novelty
- key concepts
- methodology
- findings
- important facts and claims
- limitations
- what the authors could not establish
- what could be done better
- potentially overlooked points
- practical implications
- open research questions
- recent/current advancements relevant to an older paper
- important references

Every extracted category is stored as its own knowledge partition under the same Space and source in PostgreSQL. Each stored partition record also gets a Gemini embedding in pgvector so the Space can later support semantic retrieval.

## Run

1. Put your Gemini API key in `.env`:

```text
GEMINI_API_KEY=your_key_here
```

2. Make sure Docker Desktop is running.

3. Double-click `start.bat`.

4. Open:

```text
http://127.0.0.1:8000/
```

The web UI lets you create a Space and then upload a DOCX/PDF or paste a transcript. Swagger remains available at /docs for API testing.

## API flow

Create a Space:

```text
POST /spaces
```

Upload DOCX/PDF (hard limit: 10 MB):

```text
POST /spaces/{space_id}/ingest/document
```

Paste a transcript:

```text
POST /spaces/{space_id}/ingest/transcript
```

View sources:

```text
GET /spaces/{space_id}/sources
```

View extracted knowledge:

```text
GET /spaces/{space_id}/knowledge
```

## Important V1 behavior

DOCX is parsed locally to readable text and then sent to Gemini with the fixed research-extraction prompt.

PDF text is also extracted locally for provenance/storage, but the actual PDF file is sent to Gemini so the model can work from the document itself.

Transcript input is already text, so it goes directly to Gemini.

The source file itself is not kept as a random collection of local output files. The source metadata and extracted text are stored with the source, while each structured research category is stored in its own partition record in PostgreSQL with its embedding.

The `fresh_knowledge` section is separate inside the structured result. When enabled, Gemini can use Google Search grounding to pull current information and record the resulting web sources alongside the extraction.
