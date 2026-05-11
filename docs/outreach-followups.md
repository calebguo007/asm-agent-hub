# ASM Outreach Follow-up Drafts

These are follow-up comments for existing feedback-request issues. Use them
only after 24-48 hours with no reply, and only once per thread.

## MCP Finder

Target: <https://github.com/mcpfinder/mcpfinder/issues/2>

```md
Small update: I added a live OpenRouter adapter and README GIF to make the value-metadata path more concrete:

    asm score --source openrouter 'cheap LLM under $1 per 1M tokens under 1s'

The relevant pattern for an MCP directory would be similar: index optional value metadata, expose it as facets, and rank only when a user provides preferences or hard constraints.

I am mainly looking for field-shape feedback from a discovery/search perspective. Are pricing, SLA/rate limits, quality metrics, provenance, verification, and payment/auth the right top-level facets, or would MCP Finder need a different shape?
```

## MCP Atlas

Target: <https://github.com/SamoTech/mcp-atlas/issues/1>

```md
Small update: I added a live OpenRouter adapter and a short README GIF showing the intended UX:

    asm score --source openrouter 'cheap LLM under $1 per 1M tokens under 1s'

For a reviewed registry like MCP Atlas, the piece I would value feedback on is governance rather than ranking: should value metadata be publisher-declared, curator-verified, benchmark-linked, or split into those trust levels?

ASM currently models that through provenance + `verification_status`, but I am not sure whether that is the right shape for a quality-reviewed MCP registry.
```

## Glama MCP Registry MCP Server

Target: <https://github.com/meetmatt/glama-mcp-registry-mcp-server/issues/1>

```md
Small update: I added a live OpenRouter adapter and README GIF so the aggregator use case is less abstract:

    asm score --source openrouter 'cheap LLM under $1 per 1M tokens under 1s'

For Glama-style search, I imagine ASM as optional indexing metadata rather than default ranking logic: pricing, SLA/rate limits, quality metrics, provenance, verification, and payment/auth become searchable facets, and ranking happens only when the user supplies preferences.

Does that map to how Glama structures registry/search metadata, or would the fields need to be flatter / more registry-native?
```

## Smithery CLI

Target: <https://github.com/smithery-ai/cli/issues/767>

```md
Small update: I added a live OpenRouter adapter and README GIF showing how ASM behaves as a selector rather than just a schema:

    asm score --source openrouter 'cheap LLM under $1 per 1M tokens under 1s'

For Smithery, I am not suggesting changing install/invocation semantics. The narrower question is whether optional value metadata could help users choose among servers before install or invocation: pricing, SLA/rate limits, quality metrics, provenance, verification, and payment/auth.

If this is useful, the smallest next step could be one example `server.json` with `_meta...publisher-provided.asm`, not ranking logic.
```

## Timing

- Do not post all four follow-ups at once.
- Post to MCP Finder and Glama first because their search/discovery fit is strongest.
- Wait at least 24 hours before posting to MCP Atlas and Smithery.
- Stop following up if maintainers show no interest after one follow-up.
