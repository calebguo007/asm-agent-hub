# Objective tasks coverage

Total tasks: **36**

## cost axis (11 tasks)
- ai.audio.stt
- ai.audio.tts
- ai.llm.chat
- ai.llm.embedding
- ai.video.generation
- infra.compute.gpu
- tool.automation.browser
- tool.communication.email
- tool.data.scraping
- tool.data.search
- tool.devops.deployment

## latency axis (20 tasks)
- ai.audio.stt
- ai.audio.tts
- ai.code.completion
- ai.llm.chat
- ai.llm.embedding
- ai.nlp.translation
- ai.video.generation
- ai.vision.image_generation
- infra.compute.gpu
- infra.database.postgres
- infra.database.vector
- tool.automation.browser
- tool.communication.chat
- tool.communication.email
- tool.data.scraping
- tool.data.search
- tool.devops.ci
- tool.devops.deployment
- tool.productivity.spreadsheet
- tool.productivity.todo

## quality axis (5 tasks)
- ai.audio.tts
- ai.llm.chat
- ai.llm.embedding
- ai.video.generation
- tool.productivity.todo

## Skipped (with reason)
  quality-skip ai.audio.stt: deepgram/nova@v2 no quality.metrics
  cost-skip ai.code.completion: no spread (all candidates same price or zero)
  quality-skip ai.code.completion: cursor/editor@v1 no quality.metrics
  cost-skip ai.nlp.translation: no spread (all candidates same price or zero)
  quality-skip ai.nlp.translation: deepl/translate@v2 no quality.metrics
  cost-skip ai.vision.image_generation: no spread (all candidates same price or zero)
  quality-skip ai.vision.image_generation: benchmark mismatch (FID vs GenAI_Bench_overall)
  quality-skip infra.compute.gpu: replicate/gpu-serverless@1.0 no quality.metrics
  cost-skip infra.database.postgres: no spread (all candidates same price or zero)
  quality-skip infra.database.postgres: neon/serverless-postgres@v1 no quality.metrics
  cost-skip infra.database.vector: no spread (all candidates same price or zero)
  quality-skip infra.database.vector: pinecone/index@v3 no quality.metrics
  quality-skip tool.automation.browser: benchmark mismatch (Success_Rate vs GitHub_Stars)
  cost-skip tool.communication.chat: no spread (all candidates same price or zero)
  quality-skip tool.communication.chat: discord/api@v10 no quality.metrics
  quality-skip tool.communication.email: benchmark mismatch (Delivery_Rate vs G2_Rating)
  quality-skip tool.data.scraping: firecrawl/scrape@v1 no quality.metrics
  quality-skip tool.data.search: benchmark mismatch (Semantic_Accuracy vs Relevance_Score)
  cost-skip tool.devops.ci: dimension mismatch (credit vs ci_minute)
  quality-skip tool.devops.ci: benchmark mismatch (G2_Rating vs Market_Share)
  quality-skip tool.devops.deployment: fly/machines@v1 no quality.metrics
  cost-skip tool.productivity.spreadsheet: no spread (all candidates same price or zero)
  quality-skip tool.productivity.spreadsheet: airtable/api@v1 no quality.metrics
  cost-skip tool.productivity.todo: no spread (all candidates same price or zero)
