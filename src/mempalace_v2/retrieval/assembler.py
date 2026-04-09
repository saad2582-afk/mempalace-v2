from __future__ import annotations

from typing import Any

from mempalace_v2.retrieval.query import MemoryRetriever


class MemoryAssembler:
    def __init__(self, base_dir: str):
        self.retriever = MemoryRetriever(base_dir)

    def assemble(self, prompt: str, limit: int = 5) -> dict[str, Any]:
        retrieved = self.retriever.retrieve(prompt, limit=limit)
        context_lines: list[str] = []

        if retrieved["profiles"]:
            context_lines.append("[profile]")
            for row in retrieved["profiles"]:
                context_lines.append(f"- {row['profile_type']}: {row['value']}")

        if retrieved["semantic"]:
            context_lines.append("[semantic]")
            for row in retrieved["semantic"]:
                context_lines.append(f"- {row['memory_type']} | {row['subject']} {row['predicate']} {row['value']}")

        if retrieved["tasks"]:
            context_lines.append("[tasks]")
            for row in retrieved["tasks"]:
                context_lines.append(f"- {row['status']}: {row['title']}")

        if retrieved["relationships"]:
            context_lines.append("[relationships]")
            for row in retrieved["relationships"]:
                context_lines.append(f"- {row['subject']} {row['predicate']} {row['object']}")

        return {
            "prompt": prompt,
            "retrieved": retrieved,
            "context": "\n".join(context_lines).strip(),
        }
