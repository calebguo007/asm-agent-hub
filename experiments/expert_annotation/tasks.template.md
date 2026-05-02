# Expert Annotation: 30 Service-Selection Tasks

**Instructions**:
- For each task, rank all candidates `1` (best) to `N` (worst) under the stated preference axis.
- Write **one line** in the `rationale` row explaining the top pick. Rationale is for self-discipline; it does not enter the paper.
- "trust" axis = brand reputation, security posture, signed receipts, or settlement reliability — pick whichever applies.
- Allow yourself ≤ 90 seconds per task.

After filling in, copy the rankings into `tasks.yaml` (template at the bottom).

---

## Category A: LLM / AI inference (10 tasks)

### Task 1 — Multi-turn customer support agent
**Taxonomy**: `ai.llm.chat` · **Preference axis**: `quality` · **Workload**: 200K input tokens/day, 50K output tokens/day, p99 latency tolerable up to 10s.

| Candidate | Input $/1M | Output $/1M | LMSYS Elo | p50 latency | Notes |
|---|---:|---:|---:|---:|---|
| `anthropic/claude-sonnet-4@4.0` | $3.00 | $15.00 | 1290 | 800ms | safety leader, signed receipts via PROVENANCE |
| `google/gemini-2.5-pro@2.5` | $1.25 | $5.00 | **1300** | 1.5s | cheapest input, slightly slower |
| `openai/gpt-4o@2024-11-20` | $2.50 | $10.00 | 1285 | **600ms** | fastest, mid-priced |

**Expert rank**: `[1 ,3 ,2 ]`  &nbsp;&nbsp; **Rationale**: _claude is good at writting and thinking.__

---

### Task 2 — Bulk synthetic data generation
**Taxonomy**: `ai.llm.chat` · **Preference axis**: `cost` · **Workload**: 50M input tokens/week, 50M output. Latency irrelevant (batch). Quality must be ≥ Elo 1280.

Same candidates as Task 1.

**Expert rank**: `[ 1,3 ,2 ]`  &nbsp;&nbsp; **Rationale**: _same__

---

### Task 3 — Real-time voice agent next-token streaming
**Taxonomy**: `ai.llm.chat` · **Preference axis**: `latency` · **Workload**: 100 concurrent users, p50 latency must be < 1s.

Same candidates as Task 1.

**Expert rank**: `[2 , 1, 3]`  &nbsp;&nbsp; **Rationale**: __Google have more powerful tools to connect the real world._

---

### Task 4 — RAG document embedding pipeline
**Taxonomy**: `ai.llm.embedding` · **Preference axis**: `quality` · **Workload**: 30M tokens of legal contracts to embed once. MTEB score matters.

| Candidate | $/1M tokens | MTEB avg | p50 latency | Notes |
|---|---:|---:|---:|---|
| `openai/text-embedding-3-large@3.0` | $0.13 | 64.6 | 100ms | dominant ecosystem |
| `voyageai/voyage-3-large@3.0` | $0.18 | **66.2** | 150ms | best MTEB, 50M free credits |

**Expert rank**: `[1 ,2 ]`  &nbsp;&nbsp; **Rationale**: _I'm just randomly ranked.__

---

### Task 5 — Audiobook narration (40 hours, English)
**Taxonomy**: `ai.audio.tts` · **Preference axis**: `quality` · **Workload**: ~3M characters total, voice naturalness critical.

| Candidate | $/1M chars | MOS | p50 latency | Notes |
|---|---:|---:|---:|---|
| `elevenlabs/tts-v2@2.0` | $180 | **4.5** | 400ms | premium voices |
| `openai/tts-1@1.0` | **$15** | 4.0 | 500ms | 12× cheaper |

**Expert rank**: `[ 1,2 ]`  &nbsp;&nbsp; **Rationale**: _Actually I have never used openai,but 11labs is good.__

---

### Task 6 — Real-time meeting transcription
**Taxonomy**: `ai.audio.stt` · **Preference axis**: `latency` · **Workload**: live captions, p50 must be < 500ms.

| Candidate | $/minute | p50 latency | $200 free credit | Notes |
|---|---:|---:|---|---|
| `deepgram/nova@v2` | $0.0043 | **200ms** | yes | streaming-first |
| `openai/whisper@v1` | $0.006 | 3s | no | batch-oriented |

**Expert rank**: `[ , ]`  &nbsp;&nbsp; **Rationale**: _Have no idea.__

---

### Task 7 — Marketing image generation, brand-consistent
**Taxonomy**: `ai.vision.image_generation` · **Preference axis**: `quality` · **Workload**: 500 images/month for ad creative.

| Candidate | $/image | Quality benchmark | p50 latency | Notes |
|---|---:|---:|---:|---|
| `black-forest-labs/flux-1.1-pro@1.1` | $0.04 | FID 4.8 (lower is better, COCO-30K) | 8s | independent |
| `google/imagen-3@3.0` | $0.04 | GenAI-Bench 0.72 | 10s | 50/day free |
| `openai/dall-e-3@3.0` | $0.04 (HD: $0.12) | GenEval 0.67 | 12s | tightest content policy |

**Expert rank**: `[ 3, 2, 1]`  &nbsp;&nbsp; **Rationale**: _I choose based on gptimage2 and nanobanana.__

---

### Task 8 — Image generation for high-volume internal mockups
**Taxonomy**: `ai.vision.image_generation` · **Preference axis**: `cost` · **Workload**: 5000 standard-resolution images/week.

Same candidates as Task 7. Note imagen-3 has 50/day free quota.

**Expert rank**: `[3 ,2 ,1 ]`  &nbsp;&nbsp; **Rationale**: _same__

---

### Task 9 — Short-form video generation (TikTok ads)
**Taxonomy**: `ai.video.generation` · **Preference axis**: `cost` · **Workload**: 200 × 8-second clips/week, quality must be ≥ VBench 80.

| Candidate | $/second | VBench | p50 latency | Free tier |
|---|---:|---:|---:|---|
| `google/veo-3.1@3.1` | $0.20 | **84.7** | 45s | none |
| `kuaishou/kling-3.0@3.0` | **$0.029** | 83.5 | 60s | 66 req/day |

**Expert rank**: `[1 ,2 ]`  &nbsp;&nbsp; **Rationale**: _More powerful and natural.__

---

### Task 10 — Translation API for multilingual SaaS
**Taxonomy**: `ai.nlp.translation` · **Preference axis**: `trust` · **Workload**: 20M chars/month, GDPR-sensitive customer chat.

| Candidate | $/char | p50 latency | Free tier | Notes |
|---|---:|---:|---|---|
| `deepl/translate@v2` | $0.00002 | 200ms | 500K/month | EU-based, GDPR-native |
| `google/translate@v3` | $0.00002 | **150ms** | 500K/month | broader language coverage |

**Expert rank**: `[ , ]`  &nbsp;&nbsp; **Rationale**: Don't know.___

---

## Category B: Search / Scraping / Browser (5 tasks)

### Task 11 — Research agent: deep-context web search
**Taxonomy**: `tool.data.search` · **Preference axis**: `quality` · **Workload**: 5K queries/month for an enterprise research bot.

| Candidate | $/query | Quality | p50 latency | Free tier |
|---|---:|---:|---:|---|
| `exa/search-api@v1` | $0.003 | semantic accuracy 0.95 | 600ms | 1000/month |
| `tavily/search-api@v1` | **$0.001** | relevance 0.92 | 800ms | 1000/month |

**Expert rank**: `[ , ]`  &nbsp;&nbsp; **Rationale**: _Don't know.__

---

### Task 12 — Cost-sensitive scraping for price-monitoring bot
**Taxonomy**: `tool.data.scraping` · **Preference axis**: `cost` · **Workload**: 100K pages/month, JS rendering needed.

| Candidate | $/page | p50 latency | Free tier | Notes |
|---|---:|---:|---|---|
| `firecrawl/scrape@v1` | $0.001 | 3s | 500/month | structured extraction built-in |
| `jina/reader@v1` | **$0** | **2s** | unlimited free tier | LLM-friendly markdown output |

**Expert rank**: `[ , ]`  &nbsp;&nbsp; **Rationale**: ___

---

### Task 13 — High-volume scraping for academic crawler
**Taxonomy**: `tool.data.scraping` · **Preference axis**: `latency` · **Workload**: 500K pages/week, completion time matters.

Same candidates as Task 12.

**Expert rank**: `[ , ]`  &nbsp;&nbsp; **Rationale**: ___

---

### Task 14 — Headless browser for QA of e-commerce checkouts
**Taxonomy**: `tool.automation.browser` · **Preference axis**: `quality` · **Workload**: 10K browser-minutes/month, success rate critical.

| Candidate | $/min | Success rate | p50 latency | Notes |
|---|---:|---:|---:|---|
| `browserbase/api@v1` | $0.01 | **0.96** | 2s | hosted, hardened against detection |
| `steel/browser@v1` | **$0.005** | (4.2K GitHub stars, no SR data) | **1.5s** | open-source, self-host option |

**Expert rank**: `[ , ]`  &nbsp;&nbsp; **Rationale**: ___

---

### Task 15 — Free-tier-first scraping for indie dev MVP
**Taxonomy**: `tool.data.scraping` · **Preference axis**: `trust` · **Workload**: ~200 pages/day, indie dev wants reliable + ToS-safe.

Same candidates as Task 12. Same data table.

**Expert rank**: `[ , ]`  &nbsp;&nbsp; **Rationale**: ___

---

## Category C: Storage / Database / GPU (5 tasks)

### Task 16 — Production OLTP for SaaS startup
**Taxonomy**: `infra.database.postgres` · **Preference axis**: `latency` · **Workload**: 1K req/s mixed reads/writes, p50 < 20ms.

| Candidate | $/GB-month | p50 latency | Free tier | Notes |
|---|---:|---:|---|---|
| `neon/serverless-postgres@v1` | $0 | **8ms** | 0.5GB, 1 project | branching, scale-to-zero |
| `supabase/database@v2` | $0 | 15ms | 500MB, 50K MAU | full BaaS (auth+storage included) |

**Expert rank**: `[ , ]`  &nbsp;&nbsp; **Rationale**: ___

---

### Task 17 — Greenfield app, all-in-one BaaS preferred
**Taxonomy**: `infra.database.postgres` · **Preference axis**: `trust` · **Workload**: Indie dev MVP, ecosystem matters.

Same candidates as Task 16.

**Expert rank**: `[ , ]`  &nbsp;&nbsp; **Rationale**: ___

---

### Task 18 — Vector index for production RAG, p99 < 100ms
**Taxonomy**: `infra.database.vector` · **Preference axis**: `latency` · **Workload**: 10M vectors, 200 QPS.

| Candidate | $/query | p50 latency | p99 latency | Free tier |
|---|---:|---:|---:|---|
| `pinecone/index@v3` | $0 | 20ms | 80ms | 100K vectors starter |
| `qdrant/cloud@v1` | $0 | **10ms** | **50ms** | 1GB free cluster |

**Expert rank**: `[ , ]`  &nbsp;&nbsp; **Rationale**: ___

---

### Task 19 — Vector DB for compliance-heavy enterprise
**Taxonomy**: `infra.database.vector` · **Preference axis**: `trust` · **Workload**: HIPAA + SOC2 required.

Same candidates as Task 18. Trust signals: pinecone has more SOC2/HIPAA history; qdrant offers self-hosted option.

**Expert rank**: `[ , ]`  &nbsp;&nbsp; **Rationale**: ___

---

### Task 20 — GPU inference for image-gen model fine-tune
**Taxonomy**: `infra.compute.gpu` · **Preference axis**: `cost` · **Workload**: 50K GPU-seconds/week. Must be reliable.

| Candidate | $/GPU-second | p50 latency | Cold start | Uptime |
|---|---:|---:|---:|---:|
| `replicate/gpu-serverless@1.0` | $0.000225 | 5s | 10s | 0.995 |
| `runpod/gpu-serverless@1.0` | **$0.00019** | **3s** | **6s** | **0.998** |

**Expert rank**: `[ , ]`  &nbsp;&nbsp; **Rationale**: ___

---

## Category D: Communication / Todo (5 tasks)

### Task 21 — Internal alerts to engineering team
**Taxonomy**: `tool.communication.chat` · **Preference axis**: `latency` · **Workload**: 5K alerts/day, p99 < 500ms.

| Candidate | $/message | p50 latency | Free tier | Notes |
|---|---:|---:|---|---|
| `discord/api@v10` | $0 | **80ms** | free, rate-limited | bot-friendly |
| `slack/web-api@v2` | $0 | 100ms | free 90-day history | enterprise default |

**Expert rank**: `[ , ]`  &nbsp;&nbsp; **Rationale**: ___

---

### Task 22 — Customer-facing community channel
**Taxonomy**: `tool.communication.chat` · **Preference axis**: `trust` · **Workload**: 50K MAU, business audience.

Same candidates as Task 21.

**Expert rank**: `[ , ]`  &nbsp;&nbsp; **Rationale**: ___

---

### Task 23 — Transactional email for SaaS sign-ups
**Taxonomy**: `tool.communication.email` · **Preference axis**: `quality` · **Workload**: 50K emails/month, deliverability critical.

| Candidate | $/email | Delivery rate / G2 | p50 latency | Free tier |
|---|---:|---|---:|---|
| `resend/email-api@v1` | $0.00028 | **delivery 0.985** | **300ms** | 100/day, 3K/month |
| `twilio/sendgrid@v3` | $0.00035 | G2 4.0/5 | 400ms | 100/day |

**Expert rank**: `[ , ]`  &nbsp;&nbsp; **Rationale**: ___

---

### Task 24 — Bulk newsletter, cost-first
**Taxonomy**: `tool.communication.email` · **Preference axis**: `cost` · **Workload**: 1M emails/month.

Same candidates as Task 23.

**Expert rank**: `[ , ]`  &nbsp;&nbsp; **Rationale**: ___

---

### Task 25 — Personal-task agent for power users
**Taxonomy**: `tool.productivity.todo` · **Preference axis**: `quality` · **Workload**: power user wants natural-language input + recurring tasks.

| Candidate | $/call | G2 rating | p50 latency | Pro/month |
|---|---:|---:|---:|---:|
| `google/tasks-api@v1` | $0 | 4.2 | 200ms | (free) |
| `ticktick/api@v2` | $0 | **4.5** | 150ms | $2.79 |
| `todoist/api@v2` | $0 | 4.4 | **120ms** | $4.00 |

**Expert rank**: `[ , , ]`  &nbsp;&nbsp; **Rationale**: ___

---

## Category E: DevOps / Productivity (5 tasks)

### Task 26 — CI for monorepo with 30 micro-services
**Taxonomy**: `tool.devops.ci` · **Preference axis**: `cost` · **Workload**: ~6K minutes/month.

| Candidate | Pricing model | Free tier | p50 build start | G2/share |
|---|---|---|---:|---:|
| `circleci/cloud@v2` | $0.0006/credit | 6000 credits/month | 10s | G2 4.3 |
| `github/actions@v2` | $0.008/CI-min | 2000 min/month (public unlimited) | 15s | 62% market share |

**Expert rank**: `[ , ]`  &nbsp;&nbsp; **Rationale**: ___

---

### Task 27 — CI optimised for build-start latency
**Taxonomy**: `tool.devops.ci` · **Preference axis**: `latency` · **Workload**: trunk-based dev, 80 PRs/day, want fast feedback.

Same candidates as Task 26.

**Expert rank**: `[ , ]`  &nbsp;&nbsp; **Rationale**: ___

---

### Task 28 — Deploying a stateful Rust API
**Taxonomy**: `tool.devops.deployment` · **Preference axis**: `quality` · **Workload**: long-running TCP, multi-region.

| Candidate | Pricing | p50 deploy | Notes |
|---|---|---:|---|
| `fly/machines@v1` | $3.1e-06/CPU-sec | 2s | first-class TCP, multi-region edge |
| `vercel/platform@v1` | $0/deployment hobby | **1s** | optimised for serverless web |

**Expert rank**: `[ , ]`  &nbsp;&nbsp; **Rationale**: ___

---

### Task 29 — Deploying a Next.js marketing site
**Taxonomy**: `tool.devops.deployment` · **Preference axis**: `latency` · **Workload**: 30 deploys/day, edge cache critical.

Same candidates as Task 28.

**Expert rank**: `[ , ]`  &nbsp;&nbsp; **Rationale**: ___

---

### Task 30 — Spreadsheet for non-technical PM data ops
**Taxonomy**: `tool.productivity.spreadsheet` · **Preference axis**: `trust` · **Workload**: ~2K records, PMs collaborate, share with non-technical stakeholders.

| Candidate | Pricing | p50 latency | Free tier | Notes |
|---|---|---:|---|---|
| `airtable/api@v1` | $0 | 120ms | 1000 records/base | DB-like UI, automations |
| `google/sheets-api@v4` | $0 | **100ms** | unlimited | universal, in Google Workspace |

**Expert rank**: `[ , ]`  &nbsp;&nbsp; **Rationale**: ___

---

## YAML output template

After ranking the 30 tasks above, fill in this block (then move to `tasks.yaml`):

```yaml
# tasks.yaml — expert-annotated rankings
tasks:
  - id: 1
    taxonomy: ai.llm.chat
    preference_axis: quality
    candidates: [anthropic/claude-sonnet-4@4.0, google/gemini-2.5-pro@2.5, openai/gpt-4o@2024-11-20]
    expert_rank: [?, ?, ?]   # service_ids in best-to-worst order
    rationale: ""
  - id: 2
    taxonomy: ai.llm.chat
    preference_axis: cost
    candidates: [anthropic/claude-sonnet-4@4.0, google/gemini-2.5-pro@2.5, openai/gpt-4o@2024-11-20]
    expert_rank: [?, ?, ?]
    rationale: ""
  # ... and so on for tasks 3-30
```

Or a simpler form: just give me the `expert_rank` lists in this conversation and I'll generate the YAML.
