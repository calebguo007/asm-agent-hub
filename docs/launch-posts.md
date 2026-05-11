# ASM Launch Posts

Use these posts to launch ASM as a practical CLI and MCP-compatible value
metadata layer. The first launch should lead with the OpenRouter adapter, not
with the paper.

## Hacker News

Title:

```text
Show HN: ASM - rank AI services by price, latency, quality, and provenance
```

Body:

```text
I built Agent Service Manifest (ASM), a small open protocol and CLI for value-aware AI service selection.

The practical demo: ASM can rank live OpenRouter models from public metadata:

    asm score --source openrouter 'cheap LLM under $1 per 1M tokens under 1s'

It turns provider/service metadata into comparable manifests: pricing, SLA/rate limits, quality metrics, provenance, verification, and payment/auth. The MCP integration path is intentionally lightweight: publish `.well-known/asm`, or embed ASM under MCP Registry `server.json` `_meta.io.modelcontextprotocol.registry/publisher-provided.asm`.

I am not claiming quality metrics are universally correct. The point is narrower: without structured value metadata, agent service selection is not reproducible.

Repo + demo GIF:
https://github.com/calebguo007/asm-spec
```

## Reddit / r/LocalLLaMA

Title:

```text
I built a CLI that ranks OpenRouter models by cost and constraints
```

Body:

```text
I built ASM, a small CLI/protocol experiment for choosing AI services from structured metadata instead of reading pricing pages by hand.

The part that may be useful today: it can rank OpenRouter models without writing manifests first:

    asm score --source openrouter 'cheap LLM under $1 per 1M tokens under 1s'

It builds ephemeral manifests from OpenRouter's public model metadata, applies hard constraints, and ranks candidates. The repo also has an MCP-compatible metadata format for pricing, SLA/rate limits, quality metrics, provenance, verification, and payment/auth.

Important caveat: OpenRouter's public model endpoint does not expose per-model latency, so latency constraints are reported and ignored unless strict mode is enabled. Usage ranking is treated as a revealed-preference signal, not benchmark quality.

Repo:
https://github.com/calebguo007/asm-spec

I would especially like feedback on what metadata fields are missing or wrong for real model/API selection.
```

## X / Twitter

```text
MCP tells agents what services can do.
ASM tells agents what services are worth.

I added a live OpenRouter adapter:

asm score --source openrouter 'cheap LLM under $1 per 1M tokens under 1s'

It ranks models from structured value metadata: price, constraints, provenance, and usage signals.

Repo + GIF:
https://github.com/calebguo007/asm-spec
```

## LinkedIn

```text
I have been working on Agent Service Manifest (ASM), an open protocol and CLI for value-aware service selection in agent systems.

The core idea:

MCP tells agents what services can do.
ASM tells agents what services are worth.

The latest release adds a practical OpenRouter adapter:

    asm score --source openrouter 'cheap LLM under $1 per 1M tokens under 1s'

It builds ephemeral manifests from public model metadata and ranks candidates using declared cost and preference signals. ASM also defines an MCP-compatible path through `server.json` `_meta`, so registries and aggregators can index value metadata without requiring MCP core changes.

The claim is deliberately bounded: ASM does not prove that any quality metric is universally correct. It makes value metadata computable, auditable, and reproducible.

Repo:
https://github.com/calebguo007/asm-spec
```

## 中文社区

Title:

```text
我做了一个 CLI：按价格/约束/元数据帮你选 OpenRouter 模型
```

Body:

```text
我最近在做 Agent Service Manifest (ASM)，一个给 AI service selection 用的协议和 CLI。

一句话：

MCP 告诉 agent 一个服务能做什么。
ASM 告诉 agent 一个服务值不值得调用。

现在最能直接试的是 OpenRouter adapter：

    asm score --source openrouter 'cheap LLM under $1 per 1M tokens under 1s'

它会从 OpenRouter 公开 model metadata 构造临时 manifest，然后按硬约束和偏好排序。ASM 本身定义的字段包括 pricing、SLA/rate limit、quality metric、provenance、verification、payment/auth，也可以嵌到 MCP Registry `server.json` 的 `_meta` 里。

我不想把它包装成“模型质量被证明了”。更准确的说法是：如果没有结构化 value metadata，agent 选服务这件事不可复现；ASM 是把这一步变成可计算、可审计的尝试。

Repo:
https://github.com/calebguo007/asm-spec

想听听大家觉得真实选模型/API 时还缺哪些字段。
```

## Posting Order

1. Hacker News first.
2. Reddit / r/LocalLLaMA after at least 4 hours.
3. X / Twitter and LinkedIn after the first external reaction or after 24 hours.
4. Chinese community post can go in parallel if the audience is separate.

## Accounts / Access

Do not share passwords or long-lived tokens. If Codex posts for you, use an
already logged-in browser session. GitHub repo edits can use the existing `gh`
authorization.
