---
name: sota-researcher
description: Search for authoritative materials, academic literature, expert shares, and high-quality blogs to summarize state-of-the-art (SOTA) practices for any given topic. Use when the user needs a comprehensive, high-signal overview of the latest advancements, benchmarks, or engineering standards.
---

# SOTA Researcher

This skill provides a systematic workflow for discovering and synthesizing the state-of-the-art (SOTA) in any domain.

## Research Workflow

Follow this multi-stage process to ensure high-signal results:

1. **Broad Discovery**: Perform a broad `google_web_search` to identify top-tier sources, key papers, and influential blogs.
2. **Authority Filtering**: Focus on high-authority domains (e.g., `arxiv.org`, `nature.com`, `blog.google`, `engineering.fb.com`, `medium.com` from verified experts).
3. **Deep Extraction**: Use `web_fetch` on selected high-quality URLs to extract detailed methodology, benchmarks, and "lessons learned."
4. **Library Context**: For software-related topics, use `context7` (`resolve-library-id` followed by `query-docs`) to get the latest official documentation.
5. **Synthesis**: Summarize the findings into a "SOTA Report" using the provided structure.

## Selecting Authoritative Sources

Prioritize sources in this order:
- **Academic**: `arxiv.org`, `scholar.google.com`, `nature.com`, `acm.org`.
- **Corporate Engineering Blogs**: Google AI, Meta Engineering, Netflix Tech Blog, OpenAI Blog.
- **Expert Shares**: High-signal Medium articles, GitHub repositories with significant stars/activity, or Substack newsletters from recognized industry leaders.

## SOTA Report Structure

Every report must include:
1. **Executive Summary**: A 1-2 sentence high-level overview.
2. **Current State (SOTA)**: The latest benchmarks, architectural patterns, or scientific consensus.
3. **Key Technologies/Frameworks**: The tools currently leading the field.
4. **Expert Consensus & Trends**: Observations from high-quality blogs and industry leaders.
5. **Actionable Recommendations**: Clear next steps based on the research.
6. **Sources & Citations**: Direct links to the primary materials.

## Tips for High-Signal Searching

- Use specific keywords like "state of the art", "SOTA", "2025 benchmark", "best practices", "engineering blog".
- Use `site:` operators to narrow down to top domains (e.g., `site:arxiv.org [topic]`).
- For software, search for the latest version and its breaking changes or "SOTA usage."
