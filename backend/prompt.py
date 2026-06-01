# prompt.py

SYSTEM = """You are a precise research assistant.
Answer the user's question using ONLY the context provided.

Rules:
- Cite every factual claim with [Source N] referencing the context blocks.
- If the answer is not in the context say exactly:
  "I don't have enough information in the uploaded documents to answer that."
- Be concise. Prefer bullet points for multi-part answers.
- Never invent information."""

def build_messages(query: str, chunks: list[dict],
                   history: list[dict]) -> list[dict]:
    ctx_parts = [
        f"[Source {i+1} | {c['source']} | chunk {c['chunk']} "
        f"| score {c['score']}]\n{c['text']}"
        for i, c in enumerate(chunks)
    ]
    context = "\n\n".join(ctx_parts)

    messages = [{"role": "system", "content": SYSTEM}]
    messages.extend(history[-6:])          # last 3 turns
    messages.append({
        "role": "user",
        "content": f"Context:\n{context}\n\nQuestion: {query}"
    })
    return messages