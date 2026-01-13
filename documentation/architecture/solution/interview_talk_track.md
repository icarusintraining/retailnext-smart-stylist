# Technical Talk Track: RetailNext Smart Stylist

A comprehensive technical walkthrough for presenting this solution to technical audiences.

---

## Solution Overview

RetailNext Smart Stylist is a multimodal AI fashion assistant demonstrating integration of six OpenAI APIs into a cohesive retail customer experience.

```mermaid
graph LR
    subgraph "User Inputs"
        V[Voice]
        I[Image]
        T[Text]
    end

    subgraph "OpenAI APIs"
        STT[Speech-to-Text]
        VIS[Vision API]
        SO[Structured Outputs]
        EMB[Embeddings]
        FC[Function Calling]
        TTS[Text-to-Speech]
    end

    subgraph "Output"
        R[Personalized Recommendations]
        A[Audio Response]
    end

    V --> STT
    I --> VIS
    T --> SO
    STT --> SO
    VIS --> SO
    SO --> EMB
    EMB --> FC
    FC --> R
    R --> TTS
    TTS --> A
```

---

## Three-Tier Architecture

The solution follows a clean separation of concerns across three layers.

```mermaid
graph TB
    subgraph "Tier 1: API Orchestration"
        API[FastAPI Server<br/>server.py]
        EP1["/api/chat"]
        EP2["/api/search"]
        EP3["/api/transcribe"]
        EP4["/api/tts"]
        EP5["/api/analyze-image"]
        EP6["/api/outfit-bundle"]
    end

    subgraph "Tier 2: AI Logic Layer"
        BE[Core AI Logic<br/>backend.py]
        PE[Event Parser]
        IA[Image Analyzer]
        FC[Function Calling]
        RG[Response Generator]
    end

    subgraph "Tier 3: RAG Subsystem"
        RAG[Semantic Search<br/>clothing_rag.py]
        DS[(Dataset<br/>7,500 items)]
        EC[(Embedding<br/>Cache)]
    end

    API --> EP1 & EP2 & EP3 & EP4 & EP5 & EP6
    EP1 & EP2 & EP3 & EP4 & EP5 & EP6 --> BE
    BE --> PE & IA & FC & RG
    PE & IA & FC & RG --> RAG
    RAG --> DS
    RAG --> EC
```

### Layer Responsibilities

| Layer | Component | Responsibility |
|-------|-----------|----------------|
| **Tier 1** | server.py | Request routing, validation, CORS, response formatting |
| **Tier 2** | backend.py | OpenAI API integrations, function dispatch, demo fallbacks |
| **Tier 3** | clothing_rag.py | Embedding generation, similarity search, data enrichment |

---

## API Integration Chain

Six OpenAI APIs working in sequence to process multimodal input.

```mermaid
flowchart TD
    subgraph INPUT["Input Processing"]
        direction TB
        VOICE["Voice Input"] -->|"gpt-4o-transcribe"| TRANSCRIPT["Text Transcript"]
        IMAGE["Image Upload"] -->|"GPT Vision"| ANALYSIS["Clothing Analysis"]
        TEXT["Text Input"] --> PARSE
        TRANSCRIPT --> PARSE
        ANALYSIS --> PARSE["Event Parser"]
    end

    subgraph STRUCTURED["Structured Extraction"]
        PARSE -->|"Structured Outputs"| CONTEXT["Event Context JSON"]
        CONTEXT --> |"Extracted Fields"| FIELDS["event_type<br/>formality<br/>season<br/>venue<br/>gender<br/>budget<br/>colors"]
    end

    subgraph SEARCH["Semantic Search"]
        FIELDS --> QUERY["Search Query"]
        QUERY -->|"text-embedding-3-large"| EMBED["Query Embedding"]
        EMBED --> SIM["Cosine Similarity"]
        SIM --> FILTER["Filter & Rank"]
        PRODUCTS[(Product Embeddings)] --> SIM
    end

    subgraph TOOLS["Function Calling"]
        FILTER --> TOOLS_DECISION{"Tool Selection"}
        TOOLS_DECISION -->|"check_inventory"| INV["Stock Check"]
        TOOLS_DECISION -->|"find_similar_items"| SIMILAR["Similar Items"]
        TOOLS_DECISION -->|"get_outfit_bundle"| BUNDLE["Complete Outfit"]
        TOOLS_DECISION -->|"get_item_location"| LOC["Store Location"]
    end

    subgraph OUTPUT["Response Generation"]
        INV & SIMILAR & BUNDLE & LOC --> RESPONSE["AI Response"]
        RESPONSE -->|"gpt-4o-mini-tts"| AUDIO["Audio Response"]
    end
```

---

## Multimodal Input Pipeline

Each input type follows a specialized processing path before converging.

```mermaid
flowchart LR
    subgraph VOICE_PATH["Voice Path"]
        V1[Audio Bytes] --> V2[gpt-4o-transcribe]
        V2 --> V3[Text Transcript]
    end

    subgraph IMAGE_PATH["Image Path"]
        I1[Base64 Image] --> I2[GPT Vision]
        I2 --> I3[Structured Analysis]
        I3 --> I4["clothing_type<br/>colors[]<br/>patterns<br/>style<br/>occasions[]<br/>matching_suggestions"]
    end

    subgraph TEXT_PATH["Text Path"]
        T1[User Message] --> T2[Structured Outputs]
        T2 --> T3[Event Context]
        T3 --> T4["event_type<br/>formality<br/>season<br/>venue<br/>time_of_day<br/>weather<br/>budget<br/>preferred_colors<br/>gender"]
    end

    V3 --> MERGE((Merge))
    I4 --> MERGE
    T4 --> MERGE
    MERGE --> SEARCH[Semantic Search]
```

---

## RAG System Architecture

The Retrieval Augmented Generation system for semantic product discovery.

```mermaid
flowchart TB
    subgraph INIT["Initialization (Once)"]
        CSV[(sample_styles.csv<br/>~7,500 items)] --> LOAD[Load Dataset]
        LOAD --> ENRICH["Enrich with:<br/>- Prices<br/>- Locations<br/>- Stock levels"]
        ENRICH --> GEN["Generate Embeddings<br/>text-embedding-3-large<br/>256 dimensions"]
        GEN --> CACHE[(Global Cache)]
    end

    subgraph QUERY["Query Processing"]
        Q[User Query] --> QE["Embed Query"]
        QE --> CS["Cosine Similarity<br/>vs All Products"]
        CACHE --> CS
        CS --> TH{"Threshold<br/>0.3 - 0.5"}
        TH -->|"Above"| FILTER["Apply Filters:<br/>- Gender<br/>- Category<br/>- Price range"]
        TH -->|"Below"| DISCARD[Discard]
        FILTER --> RANK["Rank by Score"]
        RANK --> TOP["Top-K Results"]
    end

    subgraph MODES["Search Modes"]
        TOP --> MODE{"Mode?"}
        MODE -->|"similar"| SIM["Find same type<br/>different colors/styles"]
        MODE -->|"complementary"| COMP["Find items that<br/>pair well together"]
    end
```

### Embedding Strategy

```mermaid
graph LR
    subgraph BATCH["Batch Processing"]
        ITEMS["7,500 Items"] --> B1["Batch 1<br/>64 items"]
        ITEMS --> B2["Batch 2<br/>64 items"]
        ITEMS --> B3["Batch 3<br/>64 items"]
        ITEMS --> BN["Batch N<br/>..."]
    end

    subgraph PARALLEL["Parallel Workers"]
        B1 & B2 & B3 & BN --> W["4 Worker Threads"]
        W --> API["OpenAI Embeddings API"]
    end

    subgraph CACHE["Caching"]
        API --> STORE["Global Cache<br/>_embeddings_cache"]
        STORE --> REUSE["Reuse on<br/>subsequent requests"]
    end
```

---

## Function Calling Pattern

Dynamic tool invocation based on conversation context.

```mermaid
flowchart TD
    USER[User Request] --> GPT["GPT with Tools"]

    GPT --> DECIDE{"Tool Needed?"}

    DECIDE -->|"Yes"| SELECT["Select Tool"]
    DECIDE -->|"No"| RESPOND["Generate Response"]

    SELECT --> DISPATCH["Function Dispatch Map"]

    DISPATCH --> T1["check_inventory()<br/>Verify stock with filters"]
    DISPATCH --> T2["find_similar_items()<br/>Semantic search"]
    DISPATCH --> T3["get_outfit_bundle()<br/>Complete outfit for occasion"]
    DISPATCH --> T4["get_item_location()<br/>Store aisle/rack/shelf"]

    T1 & T2 & T3 & T4 --> RESULT["Tool Result"]
    RESULT --> GPT

    RESPOND --> OUTPUT["Final Response"]
```

### Tool Definitions

| Tool | Purpose | Example Trigger |
|------|---------|-----------------|
| `check_inventory` | Verify stock with color/size filters | "Do you have this in blue?" |
| `find_similar_items` | Semantic search with constraints | "Something like this but cheaper" |
| `get_outfit_bundle` | Generate complete outfit | "I need a full outfit for a wedding" |
| `get_item_location` | Return store location | "Where can I find this?" |

---

## Data Flow: End-to-End Request

Complete flow from user input to response.

```mermaid
sequenceDiagram
    participant U as User
    participant F as Frontend
    participant S as Server (FastAPI)
    participant B as Backend (AI Logic)
    participant R as RAG System
    participant O as OpenAI APIs

    U->>F: Voice + Image + Text
    F->>S: POST /api/chat

    alt Has Audio
        S->>B: transcribe_audio_bytes()
        B->>O: gpt-4o-transcribe
        O-->>B: Transcript
    end

    alt Has Image
        S->>B: analyze_clothing_image()
        B->>O: GPT Vision + Schema
        O-->>B: Structured Analysis
    end

    S->>B: parse_event_context()
    B->>O: Structured Outputs
    O-->>B: Event Context JSON

    S->>R: search_by_description()
    R->>O: Embed Query
    O-->>R: Query Vector
    R->>R: Cosine Similarity
    R-->>S: Matching Products

    S->>B: process_stylist_request()
    B->>O: Chat + Function Calling

    loop Tool Calls
        O-->>B: Tool Request
        B->>B: Execute Tool
        B->>O: Tool Result
    end

    O-->>B: Final Response

    alt Audio Requested
        B->>O: gpt-4o-mini-tts
        O-->>B: Audio Bytes
    end

    B-->>S: Response Package
    S-->>F: JSON Response
    F-->>U: Display + Audio
```

---

## Response Structure

```mermaid
graph TD
    subgraph RESPONSE["API Response"]
        TR["text_response<br/>(Styled markdown)"]
        AR["audio_response_base64<br/>(MP3 bytes)"]
        EC["event_context<br/>(Parsed event details)"]
        IA["image_analysis<br/>(Clothing attributes)"]
        RI["recommended_items[]<br/>(Products with metadata)"]
        AU["apis_used[]<br/>(Tracking)"]
    end

    subgraph ITEM["Recommended Item"]
        NAME["product_name"]
        PRICE["price"]
        LOC["store_location"]
        STOCK["stock_status"]
        IMG["image_url"]
        SIM["similarity_score"]
    end

    RI --> ITEM
```

---

## Design Patterns

### Demo Mode Fallback Architecture

```mermaid
flowchart TD
    REQ[API Request] --> CHECK{"DEMO_MODE?"}

    CHECK -->|"false"| LIVE["Call OpenAI API"]
    CHECK -->|"true"| MOCK["Return Mock Data"]

    LIVE --> TRY{"Success?"}
    TRY -->|"Yes"| RESULT["Return Result"]
    TRY -->|"No"| FALLBACK["Fallback Handler"]

    FALLBACK --> MOCK
    MOCK --> RESULT

    subgraph MOCKS["Mock Data Sources"]
        M1["MOCK_INVENTORY<br/>60 curated items"]
        M2["DEMO_RESPONSES<br/>Pre-written scenarios"]
        M3["Hash-based Embeddings<br/>Deterministic vectors"]
    end

    MOCK --> MOCKS
```

### Caching Strategy

```mermaid
graph LR
    subgraph GLOBAL["Global Singletons"]
        C1["_client<br/>OpenAI Client"]
        C2["_embeddings_cache<br/>Product Vectors"]
        C3["_styles_df<br/>Dataset"]
    end

    subgraph BENEFITS["Benefits"]
        B1["Memory Efficiency"]
        B2["Fast Subsequent Requests"]
        B3["Single API Client"]
    end

    C1 --> B3
    C2 --> B2
    C3 --> B1
```

---

## OpenAI API Summary

```mermaid
graph TB
    subgraph APIS["Six OpenAI APIs"]
        direction TB
        A1["Chat Completions<br/>gpt-4.1-mini"]
        A2["Vision<br/>gpt-4.1-mini"]
        A3["Structured Outputs<br/>JSON Schema"]
        A4["Function Calling<br/>Tool Definitions"]
        A5["Embeddings<br/>text-embedding-3-large"]
        A6["Speech APIs<br/>Transcribe + TTS"]
    end

    subgraph PURPOSE["Purpose"]
        P1["Conversation & Reasoning"]
        P2["Image Analysis"]
        P3["Entity Extraction"]
        P4["Dynamic Operations"]
        P5["Semantic Search"]
        P6["Voice I/O"]
    end

    A1 --- P1
    A2 --- P2
    A3 --- P3
    A4 --- P4
    A5 --- P5
    A6 --- P6
```

---

## Scaling Considerations

```mermaid
graph TB
    subgraph CURRENT["Current Architecture"]
        C1["In-Memory Embeddings"]
        C2["Single Server"]
        C3["Global Cache"]
    end

    subgraph PRODUCTION["Production Scale"]
        P1["Vector Database<br/>(Pinecone/pgvector)"]
        P2["Horizontal Scaling<br/>(Stateless API)"]
        P3["Redis Cache<br/>(Distributed)"]
        P4["Embedding Microservice"]
    end

    C1 -.->|"Scale"| P1
    C2 -.->|"Scale"| P2
    C3 -.->|"Scale"| P3
    C1 -.->|"Extract"| P4
```

---

## Key Talking Points

1. **Multimodal Input Pipeline** - Voice, image, and text converge through specialized processing paths
2. **Structured Outputs** - JSON schema guarantees parsing reliability vs. prompt-based extraction
3. **Semantic Search** - Embeddings understand meaning, not just keywords
4. **Complementary Search** - Find items that pair together, not just similar items
5. **Function Calling** - Dynamic tool invocation based on conversation context
6. **Demo Mode** - First-class fallback system for reliable demonstrations
7. **Lazy Initialization** - Fast startup, defer expensive operations
8. **Deterministic Enrichment** - Consistent mock data across requests

---

## Anticipated Questions

| Question | Key Points |
|----------|------------|
| "How would this scale?" | Vector DB for embeddings, stateless API layer, extract embedding service |
| "Why structured outputs?" | Schema compliance guaranteed, eliminates parsing failures |
| "Why 256 dimensions?" | Tradeoff between semantic resolution and computation speed |
| "How handle API failures?" | Try/catch with fallbacks, demo mode, consistent response structure |
| "Why Python?" | First-class OpenAI SDK support, FastAPI async, rapid prototyping |
