# Model Selection Rationale & Trade-off Analysis

This document provides deep explanations for model choices in the RetailNext Smart Stylist project, including comparison tables against alternative models, and guidance on data sovereignty for regulated Australian customers.

---

## Table of Contents
1. [Models Used in This Project](#models-used-in-this-project)
2. [Chat/Reasoning Model Analysis](#chatreasoning-model-analysis)
3. [Speech-to-Text Model Analysis](#speech-to-text-model-analysis)
4. [Text-to-Speech Model Analysis](#text-to-speech-model-analysis)
5. [Embedding Model Analysis](#embedding-model-analysis)
6. [Why We Didn't Use Certain Models](#why-we-didnt-use-certain-models)
7. [Data Sovereignty & Regional Deployment](#data-sovereignty--regional-deployment)
8. [Talking Points for Interview](#talking-points-for-interview)

---

## Models Used in This Project

| Capability | Model Used | Alternative Considered |
|------------|------------|----------------------|
| Chat + Vision | `gpt-4o` | GPT-4.1, o1, o3 |
| Speech-to-Text | `gpt-4o-transcribe` | Whisper, gpt-4o-mini-transcribe |
| Text-to-Speech | `gpt-4o-mini-tts` | Realtime API, tts-1, tts-1-hd |
| Embeddings | `text-embedding-3-large` | text-embedding-3-small, ada-002 |
| Structured Outputs | `gpt-4o` | GPT-4.1 (better), gpt-4o-mini |

---

## Chat/Reasoning Model Analysis

### Current Choice: GPT-4o

**Why we chose GPT-4o:**
- Unified multimodal model (text + vision in one call)
- Proven reliability for function calling
- Good balance of capability vs cost
- 128K context window sufficient for retail conversations

### Complete Model Comparison Table (All OpenAI Models)

| Model | Input Cost | Output Cost | Context | Latency | Tool Calling | Vision | Best For |
|-------|------------|-------------|---------|---------|--------------|--------|----------|
| **gpt-4o** (current) | $2.50/1M | $10.00/1M | 128K | Medium | Good | Yes | Multimodal, general |
| gpt-4o-mini | $0.15/1M | $0.60/1M | 128K | Low | Good | Yes | Simple tasks |
| **GPT-4.1** | $2.00/1M | $8.00/1M | **1M** | Low | **Excellent** | Yes | Production workloads |
| **GPT-4.1-mini** | $0.40/1M | $1.60/1M | **1M** | **Very Low** | **Excellent** | Yes | **RECOMMENDED** |
| **GPT-4.1-nano** | $0.10/1M | $0.40/1M | **1M** | **Fastest** | Good | No | Classification, autocomplete |
| o1 | $15.00/1M | $60.00/1M | 200K | High | Limited | No | Complex reasoning |
| o3 | $10.00/1M | $40.00/1M | 200K | High | Limited | No | Deep analysis |

### Latency Benchmarks (Time to First Token)

| Model | Latency (128K context) | Latency (simple query) |
|-------|------------------------|------------------------|
| GPT-4.1-nano | **< 5 seconds** | ~200ms |
| GPT-4.1-mini | ~550ms | ~300ms |
| gpt-4o-mini | 10-20 seconds | ~500ms |
| GPT-4o | 15-30 seconds | ~800ms |
| GPT-4.1 | ~1 second | ~500ms |

### Benchmark Performance Comparison

| Model | MMLU | GPQA | Aider Coding | Tool Calling |
|-------|------|------|--------------|--------------|
| GPT-4.1-nano | 80.1% | 50.3% | 9.8% | Good |
| GPT-4.1-mini | Higher | Higher | Higher | **Excellent** |
| gpt-4o-mini | Lower than nano | Lower | Lower | Good |
| GPT-4o | ~85% | ~55% | ~15% | Good |
| GPT-4.1 | ~88% | ~58% | ~20% | **Excellent** |

**Key Finding:** GPT-4.1-nano scores **higher than gpt-4o-mini** on MMLU, GPQA, and Aider coding benchmarks while being 33% cheaper.

---

## DEFINITIVE RECOMMENDATION: Migrate to GPT-4.1-mini

### Why GPT-4.1-mini is the Ideal Choice for RetailNext

| Aspect | GPT-4o (Current) | GPT-4.1-mini (Recommended) | Improvement |
|--------|------------------|---------------------------|-------------|
| **Input Cost** | $2.50/1M | $0.40/1M | **84% cheaper** |
| **Output Cost** | $10.00/1M | $1.60/1M | **84% cheaper** |
| **Context Window** | 128K | 1M | **8x larger** |
| **Latency** | ~800ms | ~300ms | **62% faster** |
| **Tool Calling** | Good | Excellent (30% more efficient) | Better |
| **Instruction Following** | Good | Excellent | Better |
| **Vision** | Yes | Yes | Same |
| **Structured Outputs** | Yes | Yes | Same |

### Cost Savings Calculation

**Current (GPT-4o) - Per Conversation:**
- ~1,000 input tokens × $2.50/1M = $0.0025
- ~500 output tokens × $10.00/1M = $0.0050
- **Total: ~$0.0075 per chat call**

**With GPT-4.1-mini - Per Conversation:**
- ~1,000 input tokens × $0.40/1M = $0.0004
- ~500 output tokens × $1.60/1M = $0.0008
- **Total: ~$0.0012 per chat call**

**Savings: 84% cost reduction per conversation**

### When to Use Each Model

| Use Case | Recommended Model | Reason |
|----------|-------------------|--------|
| **Main Chat + Recommendations** | GPT-4.1-mini | Best balance of cost, speed, quality |
| **Vision/Image Analysis** | GPT-4.1-mini or GPT-4o | Both support vision |
| **Simple Classification** | GPT-4.1-nano | Fastest, cheapest |
| **Complex Styling Advice** | GPT-4.1 | Highest quality |
| **Event Context Parsing** | GPT-4.1-mini | Fast structured outputs |

### Should We Use GPT-4.1-nano?

**For most retail queries: No.** Here's why:

| Aspect | GPT-4.1-nano | GPT-4.1-mini | Verdict |
|--------|--------------|--------------|---------|
| Cost | $0.10/$0.40 | $0.40/$1.60 | Nano 4x cheaper |
| Speed | Fastest | Very Fast | Nano faster |
| Tool Calling | Good (has quirks) | Excellent | **Mini better** |
| Quality | Good | Excellent | **Mini better** |
| Vision | **No** | Yes | **Mini required** |
| Parallel Tool Calls | Issues reported | Works well | **Mini better** |

**GPT-4.1-nano is best for:**
- Simple classification ("Is this formal or casual?")
- Autocomplete suggestions
- Content extraction from long documents
- Pre-filtering queries before sending to larger model

**GPT-4.1-nano is NOT ideal for:**
- Multi-turn conversations
- Complex tool orchestration (our function calling)
- Vision/image analysis (not supported)
- Quality-critical recommendations

### Recommended Hybrid Approach

```python
def select_model(query: str, has_image: bool, complexity: str) -> str:
    """Intelligent model routing for cost optimization."""

    if has_image:
        # Vision required - must use 4.1-mini or higher
        return "gpt-4.1-mini"

    if complexity == "simple":
        # Simple queries: "Show me blue shirts"
        return "gpt-4.1-nano"  # Fastest, cheapest

    if complexity == "standard":
        # Most retail queries
        return "gpt-4.1-mini"  # Best balance

    if complexity == "complex":
        # Complex styling: complete outfit, multiple requirements
        return "gpt-4.1"  # Highest quality

    return "gpt-4.1-mini"  # Default
```

### Migration Path

**Phase 1: Replace gpt-4o with gpt-4.1-mini**
```python
# Change in backend.py line 34
GPT_MODEL = os.getenv("OPENAI_GPT_MODEL", "gpt-4.1-mini")  # Was "gpt-4o"
```

**Phase 2: Add model routing (optional)**
- Route simple queries to gpt-4.1-nano
- Keep vision queries on gpt-4.1-mini
- Escalate complex queries to gpt-4.1

**Expected Results:**
- 84% cost reduction
- 62% latency improvement
- Equal or better quality (GPT-4.1-mini beats GPT-4o on benchmarks)

### Talking Point for Interview

> "Looking at the current OpenAI model lineup, I'd recommend migrating from GPT-4o to GPT-4.1-mini. It's 84% cheaper, 62% faster, has an 8x larger context window, and actually scores higher on benchmarks including tool calling. The only trade-off is it's slightly newer, but OpenAI is positioning GPT-4.1 as the production-ready successor. For our retail use case, GPT-4.1-nano is tempting at $0.10/1M tokens, but it lacks vision support and has some quirks with parallel tool calls. GPT-4.1-mini hits the sweet spot."

---

## Speech-to-Text Model Analysis

### Current Choice: gpt-4o-transcribe

**Why we chose gpt-4o-transcribe:**
- 90% fewer hallucinations vs Whisper in noisy environments
- Better accent handling (critical for Australian market)
- Superior Word Error Rate (WER) on benchmarks

### Comparison Table: STT Models

| Model | Cost per Minute | Cost per Hour | Latency | WER | Languages | Best For |
|-------|-----------------|---------------|---------|-----|-----------|----------|
| **gpt-4o-transcribe** (used) | $0.006 | $0.36 | ~320ms | ~8.9% | 100+ | Production accuracy |
| **gpt-4o-mini-transcribe** | $0.003 | $0.18 | ~200ms | ~11% | 100+ | **Cost-sensitive** |
| whisper-1 | $0.006 | $0.36 | ~400ms | ~12-15% | 50+ | Legacy |

### Recommendation: Consider gpt-4o-mini-transcribe

For a retail environment with clear audio (not extremely noisy), **gpt-4o-mini-transcribe** offers:
- 50% cost savings ($0.003 vs $0.006 per minute)
- Faster latency (~200ms vs ~320ms)
- Acceptable WER for retail queries (~11% vs ~8.9%)

**Keep gpt-4o-transcribe for:**
- Very noisy environments
- Strong Australian accents
- Critical accuracy requirements

### Key Advantages of gpt-4o-transcribe

| Capability | gpt-4o-transcribe | whisper-1 |
|------------|-------------------|-----------|
| Hallucination rate (noisy) | Very Low | Moderate |
| Australian accent handling | Excellent | Good |
| Background noise tolerance | Excellent | Moderate |
| Word Error Rate (Common Voice) | 8.9% | 12-15% |
| API compatibility | Same as Whisper | N/A |

**Talking Point:**
> "For a retail environment with ambient noise and Australian accents, gpt-4o-transcribe was the clear choice. It has 90% fewer hallucinations in noisy environments compared to Whisper, which is critical when customers are speaking in a busy store."

### Could We Use gpt-4o-mini-transcribe?

**Yes, consider for cost optimization:**
- 50% cheaper ($3 vs $6 per 1000 minutes)
- Slightly higher WER but acceptable for most retail queries
- Good for clear audio environments

---

## Text-to-Speech Model Analysis

### Current Choice: gpt-4o-mini-tts

**Why we chose gpt-4o-mini-tts:**
- **Instruction-steered voice control** - can specify Australian accent via prompt
- Cost-effective for non-realtime use
- Natural, conversational output

### Comparison Table: TTS Models

| Model | Input Cost | Output Cost | Est. Cost/Min | Latency | Voice Control | Best For |
|-------|------------|-------------|---------------|---------|---------------|----------|
| **gpt-4o-mini-tts** (used) | $0.60/1M chars | $12.00/1M audio tokens | ~$0.015 | Medium | **Full instruction steering** | Custom accents |
| tts-1 | $15.00/1M chars | - | ~$0.015 | Low | None | Simple, fast |
| tts-1-hd | $30.00/1M chars | - | ~$0.030 | Medium | None | High quality |
| Realtime API | $4.00/1M text | $64.00/1M audio tokens | ~$0.24 | **Very Low** | Full | Live conversation |

**Key insight:** gpt-4o-mini-tts costs about the same as tts-1 (~$0.015/minute) but adds instruction steering for accents and tones.

### The Instruction-Steering Advantage

This is the killer feature of gpt-4o-mini-tts:

```python
response = client.audio.speech.create(
    model="gpt-4o-mini-tts",
    voice="nova",
    input=text,
    instructions="""
        Speak with a warm, friendly Australian accent.
        Use natural Australian intonation and pacing.
        Sound like a helpful retail assistant in Melbourne or Sydney.
    """
)
```

**What you can control:**
- Accent (Australian, British, American, etc.)
- Emotional tone (warm, professional, enthusiastic)
- Pacing (fast, slow, measured)
- Style (conversational, formal, whispered)

**Talking Point:**
> "The instruction-steered TTS is a differentiator for RetailNext. We can match the brand voice exactly - a friendly Australian retail assistant - without pre-recording voices or limiting to fixed options. This same system could easily adapt to different regional stores or brand personas."

### Why Not the Realtime API?

| Aspect | gpt-4o-mini-tts (Used) | Realtime API |
|--------|------------------------|--------------|
| Cost (audio output) | $12/1M chars | $64/1M tokens (~$0.24/min) |
| Latency | ~500ms | ~100ms |
| Use Case | Request/response | Live conversation |
| Complexity | Simple HTTP | WebSocket/WebRTC |
| Best For | Retail kiosk | Phone agents, live support |

**Talking Point:**
> "The Realtime API is impressive for live voice conversations, but it's 5x more expensive and adds WebSocket complexity. For a retail kiosk where 500ms latency is acceptable, our approach is more cost-effective. If RetailNext wanted live phone support, we'd consider Realtime."

---

## Embedding Model Analysis

### Current Choice: text-embedding-3-large (256 dimensions)

**Why this configuration:**
- Best quality embeddings available
- Reduced to 256 dimensions for efficiency
- Excellent for fashion semantic similarity

### Comparison Table: Embedding Models

| Model | Cost (per 1M tokens) | Dimensions | Quality (MTEB) | Best For |
|-------|---------------------|------------|----------------|----------|
| **text-embedding-3-large** (used) | $0.13 | 256-3072 | 64.6% | Highest quality, flexible |
| text-embedding-3-small | $0.02 | 512-1536 | 62.3% | Cost-sensitive |
| text-embedding-ada-002 | $0.10 | 1536 | 61.0% | Legacy |

### Why 256 Dimensions?

text-embedding-3-large supports **Matryoshka Representation Learning** - you can truncate embeddings to any dimension with minimal quality loss.

| Dimensions | Vector Size | Quality Retention | Use Case |
|------------|-------------|-------------------|----------|
| 3072 (max) | 12KB | 100% | Highest precision needs |
| 1536 | 6KB | ~99% | General purpose |
| **256 (used)** | 1KB | ~95% | Fast similarity, large catalogs |

**Trade-offs at 256 dimensions:**
- 12x smaller vectors than max
- 12x faster cosine similarity computation
- 12x less memory usage
- ~5% quality reduction (acceptable for fashion)

**Talking Point:**
> "We use text-embedding-3-large at 256 dimensions - a deliberate trade-off. For fashion similarity, we don't need the full 3072 dimensions. At 256, we get 95% of the quality with 12x faster search. For a catalog of millions of items, this makes the difference between sub-second and multi-second responses."

### Could We Use text-embedding-3-small?

**Yes, for cost optimization:**
- 6x cheaper ($0.02 vs $0.13 per 1M tokens)
- 2% lower quality on benchmarks
- Acceptable for most retail use cases

---

## Why We Didn't Use Certain Models

### GPT-5 / GPT-5.2
| Reason | Explanation |
|--------|-------------|
| Availability | Not generally available in API at project time |
| Cost | Significantly higher pricing |
| Overkill | Fashion recommendations don't need frontier reasoning |
| Latency | Larger models = slower responses |

### o1 / o3 Reasoning Models
| Reason | Explanation |
|--------|-------------|
| Cost | o1: $15/$60, o3: $10/$40 per 1M tokens (10x GPT-4o) |
| Latency | Extended "thinking" time (seconds to minutes) |
| Use Case Mismatch | Designed for complex reasoning, not conversational retail |
| When to Use | Mathematical proofs, code generation, complex analysis |

**Talking Point:**
> "o1 and o3 are incredible for complex reasoning - solving math olympiad problems or analyzing legal contracts. But for retail conversations, they're overkill. A customer asking 'what shoes match this dress?' doesn't need multi-step reasoning chains. GPT-4o handles this perfectly at 1/10th the cost."

### Realtime Voice API
| Reason | Explanation |
|--------|-------------|
| Cost | $32/$64 per 1M audio tokens vs $6-12 for separate STT/TTS |
| Complexity | WebSocket/WebRTC vs simple HTTP |
| Use Case | Best for live phone agents, not retail kiosks |
| When to Use | If RetailNext wants AI phone support |

### Whisper (vs gpt-4o-transcribe)
| Reason | Explanation |
|--------|-------------|
| Accuracy | gpt-4o-transcribe has 90% fewer hallucinations |
| Accent Handling | Better Australian accent recognition |
| Same Cost | Both $6/1000 minutes |
| Conclusion | No reason to use Whisper anymore |

---

## Data Sovereignty & Regional Deployment

### Critical Question for Australian Regulated Customers

> "Does OpenAI have any models that are onshore/locally deployed in Australia?"

### The Answer: OpenAI Direct API - No

**OpenAI's direct API does not offer regional deployment.** All API calls are processed in OpenAI's infrastructure (primarily US-based).

For regulated Australian customers requiring data sovereignty, the solution is **Azure OpenAI Service**.

### Azure OpenAI Australia Options

| Deployment Type | Data Residency | Available In Australia |
|----------------|----------------|----------------------|
| Standard Regional | Australia East (Sydney) | Yes |
| Standard Regional | Australia Southeast (Melbourne) | Yes |
| Global | Processed anywhere | Yes (but data crosses borders) |
| Data Zone | Within specified zone | US/EU only currently |

### What Azure OpenAI Offers in Australia

| Capability | Azure OpenAI (Australia) | OpenAI Direct API |
|------------|-------------------------|-------------------|
| Data at Rest | Australia | US |
| Inference Processing | Australia (Standard Regional) | US |
| Data Sovereignty | Meets Australian requirements | Does not |
| Models Available | GPT-4o, GPT-4, Embeddings | All models |
| Compliance | IRAP, ISO 27001, SOC 2 | SOC 2 |

### Azure OpenAI Regional Deployment in Australia

**To ensure data stays in Australia:**

1. **Choose "Standard" deployment type** (not "Global")
2. **Select Australia East or Australia Southeast region**
3. **All inference happens locally in Sydney/Melbourne**

```python
# Azure OpenAI with Australian data residency
from openai import AzureOpenAI

client = AzureOpenAI(
    azure_endpoint="https://your-resource.openai.azure.com",
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    api_version="2024-02-15-preview"
)

# Data never leaves Australia
response = client.chat.completions.create(
    model="gpt-4o",  # deployment name
    messages=[...]
)
```

### Microsoft's 2025 Sovereign Cloud Announcements

Microsoft announced in late 2025:
- **Australia** is one of 4 initial countries for in-country AI processing
- Microsoft 365 Copilot interactions can be processed entirely in Australia
- Azure OpenAI endpoints in Australia East/Southeast process locally

### Talking Points for Regulated Customers

**If the CTO asks about data sovereignty:**

> "Great question - data sovereignty is critical for regulated industries. OpenAI's direct API doesn't offer regional deployment, but Azure OpenAI does. We can deploy this exact solution using Azure OpenAI in Australia East, ensuring:
>
> 1. All data at rest stays in Sydney
> 2. All inference processing happens in Australia
> 3. Compliance with Australian privacy requirements
> 4. Same GPT-4o capabilities, same code
>
> Microsoft announced in 2025 that Australia is one of the first countries for their sovereign AI initiatives. The only change to our code would be switching from `OpenAI()` to `AzureOpenAI()` client."

### Comparison: OpenAI Direct vs Azure OpenAI

| Aspect | OpenAI Direct API | Azure OpenAI (Australia) |
|--------|-------------------|-------------------------|
| Data Location | US | Australia |
| IRAP Compliance | No | Yes |
| Australian Privacy Act | Requires assessment | Compliant |
| Model Availability | All models, day 1 | Some delay (weeks) |
| Pricing | OpenAI pricing | Azure pricing (similar) |
| SLA | 99.9% | 99.9% |
| Support | OpenAI support | Microsoft support |
| Enterprise Features | Limited | Full Azure integration |

### Code Change for Azure OpenAI

**Current (OpenAI Direct):**
```python
from openai import OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
```

**For Australian Data Sovereignty (Azure):**
```python
from openai import AzureOpenAI
client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    api_version="2024-02-15-preview"
)
```

**The rest of the code is identical** - same `client.chat.completions.create()`, same function calling, same everything.

---

## Talking Points for Interview

### On Model Selection Philosophy

> "Model selection isn't about using the newest or most powerful - it's about matching capability to use case at the right cost point. For retail conversations, GPT-4o hits the sweet spot: multimodal capability, reliable function calling, and reasonable latency. Using o3 would be like using a Formula 1 car for grocery shopping."

### On Cost Optimization

> "Our current cost is about $0.03-0.05 per conversation. We could cut this further by:
> 1. Routing simple queries to gpt-4o-mini (10x cheaper)
> 2. Using text-embedding-3-small (6x cheaper)
> 3. Caching common embeddings
>
> But even at current costs, with a 25% basket size increase generating $30 additional revenue, the ROI is 600:1."

### On Future-Proofing

> "The architecture is model-agnostic. When GPT-5 or better models arrive, we change one environment variable. The function calling interface, structured outputs schema, and RAG pipeline all remain unchanged. That's deliberate - we built for flexibility."

### On Latency vs Quality

> "There's always a trade-off between response quality and speed. We chose:
> - gpt-4o over gpt-4o-mini: Better recommendations worth the extra 200ms
> - 256-dim embeddings over 3072: Faster search, minimal quality loss
> - Request/response TTS over Realtime: Simpler, cheaper, acceptable latency
>
> Each decision was conscious, not default."

### On Data Sovereignty

> "This is a solved problem. Azure OpenAI Service in Australia East gives us identical capabilities with guaranteed data residency. For regulated customers - banking, healthcare, government - we switch to Azure deployment with a one-line code change. The architecture already supports it."

---

## Summary: Model Choices Justified

| Choice | Justification | Alternative If Needed |
|--------|---------------|----------------------|
| GPT-4o for chat | Multimodal, reliable, cost-effective | GPT-4.1 for better instruction following |
| gpt-4o-transcribe | Best accuracy, accent handling | gpt-4o-mini-transcribe for 50% cost savings |
| gpt-4o-mini-tts | Instruction steering for Australian accent | Realtime API for live conversations |
| text-embedding-3-large @ 256d | Best quality, optimized dimensions | text-embedding-3-small for 6x cost savings |
| Structured Outputs | 100% schema reliability | JSON mode (not recommended) |

**Bottom Line:** Every model choice is defensible, optimized for the retail use case, and has a clear upgrade/downgrade path based on customer requirements.

---

## Final Analysis: Is GPT-4o the Best Choice?

### The Verdict: No. GPT-4.1-mini is Better.

After comprehensive analysis of all OpenAI models, **GPT-4o is NOT the optimal choice** for the RetailNext Smart Stylist. Here's the definitive comparison:

### Complete Cost Analysis: Current vs Optimal

| Component | Current Model | Optimal Model | Savings |
|-----------|--------------|---------------|---------|
| Chat/Vision | gpt-4o ($2.50/$10.00) | **gpt-4.1-mini** ($0.40/$1.60) | **84%** |
| Transcription | gpt-4o-transcribe ($0.006/min) | gpt-4o-mini-transcribe ($0.003/min) | **50%** |
| TTS | gpt-4o-mini-tts ($0.015/min) | gpt-4o-mini-tts ($0.015/min) | 0% (already optimal) |
| Embeddings | text-embedding-3-large | text-embedding-3-large | 0% (already optimal) |

### Per-Conversation Cost Breakdown

**Current Implementation (GPT-4o):**
| Component | Tokens/Usage | Cost |
|-----------|--------------|------|
| Chat input | ~1,500 tokens | $0.00375 |
| Chat output | ~800 tokens | $0.008 |
| RAG embedding | ~200 tokens | $0.000026 |
| Transcription | ~30 seconds | $0.003 |
| TTS | ~60 seconds | $0.015 |
| **Total** | | **~$0.030** |

**Optimized Implementation (GPT-4.1-mini):**
| Component | Tokens/Usage | Cost |
|-----------|--------------|------|
| Chat input | ~1,500 tokens | $0.0006 |
| Chat output | ~800 tokens | $0.00128 |
| RAG embedding | ~200 tokens | $0.000026 |
| Transcription | ~30 seconds | $0.0015 |
| TTS | ~60 seconds | $0.015 |
| **Total** | | **~$0.018** |

**Savings: 40% cost reduction per conversation**

### Why GPT-4.1-mini Beats GPT-4o

| Metric | GPT-4o | GPT-4.1-mini | Winner |
|--------|--------|--------------|--------|
| Input Cost | $2.50/1M | $0.40/1M | **4.1-mini (6x cheaper)** |
| Output Cost | $10.00/1M | $1.60/1M | **4.1-mini (6x cheaper)** |
| Context Window | 128K | 1M | **4.1-mini (8x larger)** |
| Latency | ~800ms | ~300ms | **4.1-mini (62% faster)** |
| Tool Calling | Good | Excellent | **4.1-mini** |
| Instruction Following | Good | Excellent | **4.1-mini** |
| Vision Support | Yes | Yes | Tie |
| Structured Outputs | Yes | Yes | Tie |
| Benchmarks (MMLU) | ~85% | Higher | **4.1-mini** |

### Why NOT GPT-4.1-nano

Despite being the cheapest ($0.10/$0.40), GPT-4.1-nano is **not recommended** as the primary model because:

1. **No Vision Support** - Cannot analyze uploaded clothing images
2. **Tool Calling Quirks** - Can generate duplicate tool calls
3. **Lower Quality** - Less capable at nuanced fashion recommendations
4. **Limited Testing** - Some independent tests show underwhelming results

**Use nano only for:** Pre-classification, autocomplete, or simple queries without images.

### Final Recommendation

```
┌─────────────────────────────────────────────────────────────────┐
│  RECOMMENDED PRODUCTION CONFIGURATION                           │
├─────────────────────────────────────────────────────────────────┤
│  Chat/Vision:     gpt-4.1-mini     (84% cheaper, faster)       │
│  Transcription:   gpt-4o-mini-transcribe (50% cheaper)         │
│  TTS:             gpt-4o-mini-tts  (already optimal)           │
│  Embeddings:      text-embedding-3-large @ 256d (already opt.) │
├─────────────────────────────────────────────────────────────────┤
│  Expected Savings: 40% per conversation                         │
│  Expected Latency: 50%+ faster                                  │
│  Quality Impact:   Equal or better                              │
└─────────────────────────────────────────────────────────────────┘
```

### One-Line Code Change

```python
# backend.py line 34
GPT_MODEL = os.getenv("OPENAI_GPT_MODEL", "gpt-4.1-mini")  # Changed from "gpt-4o"

# backend.py line 36
TRANSCRIPTION_MODEL = os.getenv("OPENAI_TRANSCRIBE_MODEL", "gpt-4o-mini-transcribe")  # Changed from "gpt-4o-transcribe"
```

### Interview Talking Point

> "After analyzing the full OpenAI model portfolio, I'd recommend migrating from GPT-4o to GPT-4.1-mini. It's 84% cheaper for the chat model alone, 62% faster, and actually outperforms GPT-4o on benchmarks. Combined with switching transcription to gpt-4o-mini-transcribe, we'd see a 40% reduction in per-conversation costs while improving response time. The architecture supports this change with a single environment variable - no code refactoring required. GPT-4.1-nano at $0.10/1M is tempting, but it lacks vision support which we need for image analysis. GPT-4.1-mini is the sweet spot for retail applications."

---

## Sources

- [OpenAI Pricing](https://openai.com/api/pricing/)
- [OpenAI Models Documentation](https://platform.openai.com/docs/models)
- [GPT-4.1 Introduction](https://openai.com/index/gpt-4-1/)
- [Azure OpenAI Data Residency](https://azure.microsoft.com/en-us/explore/global-infrastructure/data-residency)
- [Microsoft Sovereign Cloud Announcement](https://azure.microsoft.com/en-us/blog/microsoft-strengthens-sovereign-cloud-capabilities-with-new-services/)
- [OpenAI Audio Models Introduction](https://openai.com/index/introducing-our-next-generation-audio-models/)
- [OpenAI Realtime API](https://openai.com/index/introducing-the-realtime-api/)
- [OpenAI Structured Outputs](https://openai.com/index/introducing-structured-outputs-in-the-api/)
