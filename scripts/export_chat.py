#!/usr/bin/env python3
"""Exporteert een Pi-sessie (JSONL) naar een leesbaar Markdown-transcript.

Gebruik:  python3 export_chat.py <sessie.jsonl> <uitvoer.md>
Houdt zich aan de "AI-chat als bijlage"-regel: prompts (user) + output (assistant)
+ het toolgebruik, in leesbare vorm. Systeem-prompts en interne metadata worden
niet meegegeven.
"""
import json
import sys
from datetime import datetime


def load(path):
    entries = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return entries


def active_branch(entries):
    """Volgt de actuele tak van blad terug naar wortel, en keert die om."""
    by_id = {e.get("id"): e for e in entries if e.get("id")}
    children = {}
    for e in entries:
        pid = e.get("parentId")
        if pid is not None:
            children.setdefault(pid, []).append(e.get("id"))
    # blad = een entry die door niemand als ouder wordt gebruikt
    leaves = [eid for eid in by_id if eid not in children]
    if not leaves:
        return list(entries)
    # laatste geschreven blad gebruiken
    leaf = max((by_id[l] for l in leaves), key=lambda e: e.get("timestamp", ""))
    path = []
    cur = leaf.get("id")
    while cur is not None and cur in by_id:
        path.append(by_id[cur])
        cur = by_id[cur].get("parentId")
    path.reverse()
    return path


def ts(entry):
    t = entry.get("timestamp", "")
    try:
        return datetime.fromisoformat(t.replace("Z", "+00:00")).strftime("%Y-%m-%d %H:%M")
    except Exception:
        return t


def text_of(content):
    """Normaleert message.content naar plain text."""
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for b in content:
            if isinstance(b, dict):
                if b.get("type") == "text" and b.get("text"):
                    parts.append(b["text"])
                elif b.get("type") == "thinking" and b.get("thinking"):
                    pass  # redenering weglaten in transcript
                elif b.get("type") == "toolCall" or b.get("type") == "tool_use":
                    pass
        return "\n".join(p for p in parts if p)
    return str(content)


def tool_calls_of(content):
    if not isinstance(content, list):
        return []
    calls = []
    for b in content:
        if isinstance(b, dict) and (b.get("type") == "toolCall" or b.get("type") == "tool_use"):
            name = b.get("name") or b.get("toolName") or "?"
            args = b.get("arguments") or b.get("args") or b.get("input") or {}
            calls.append((name, args))
    return calls


def summarize_args(args):
    """Korte, leesbare samenvatting van tool-argumenten."""
    if not isinstance(args, dict):
        s = str(args)
        return s[:160] + ("…" if len(s) > 160 else "")
    hints = []
    for key in ("path", "command", "action", "query", "code", "edits", "content"):
        if key in args:
            v = args[key]
            if isinstance(v, str):
                hints.append(f"{key}={v[:80]}{'…' if len(v) > 80 else ''}")
            elif key == "edits":
                hints.append(f"edits={len(v)} wijziging(en)")
            elif key == "code":
                hints.append(f"code=({len(v)} tekens)")
            elif key == "content":
                hints.append(f"content=({len(v)} tekens)")
            else:
                hints.append(f"{key}={v}")
    if hints:
        return " · ".join(hints)
    s = json.dumps(args, ensure_ascii=False)
    return s[:160] + ("…" if len(s) > 160 else "")


def main():
    src, dst = sys.argv[1], sys.argv[2]
    entries = load(src)
    branch = active_branch(entries)

    header = next((e for e in entries if e.get("type") == "session"), {})
    model = next((e for e in entries if e.get("type") == "model_change"), {})
    provider = model.get("provider", "?")
    model_id = model.get("modelId", "?")

    out = []
    out.append("# AI-chat — Trendreis (volledige sessie)")
    out.append("")
    out.append(f"> Export uit de Pi-sessie `{header.get('id','?')}` — "
               f"werkmap `{header.get('cwd','?')}`  ")
    out.append(f"> Model: **{provider}/{model_id}** (lokaal via Ollama)  ")
    out.append(f"> Sessie gestart: {header.get('timestamp','?')}  ")
    out.append("> ")
    out.append("> Dit is de volledige AI-chat (prompts én output) die is gebruikt voor dit "
               "project, per de HAN-richtlijn als bijlage. Systeem-prompts en interne "
               "metadata zijn weggelaten; het gesprek en het toolgebruik staan er.")
    out.append("")
    out.append("---")
    out.append("")

    n_user = n_asst = n_tool = 0
    for e in branch:
        if e.get("type") != "message":
            continue
        msg = e.get("message", {})
        role = msg.get("role")
        if role == "system":
            continue
        if role == "user":
            body = text_of(msg.get("content")).strip()
            if not body:
                continue
            n_user += 1
            out.append(f"## 👤 Prompt — {ts(e)}")
            out.append("")
            out.append(body)
            out.append("")
        elif role == "assistant":
            body = text_of(msg.get("content")).strip()
            calls = tool_calls_of(msg.get("content"))
            if not body and not calls:
                continue
            n_asst += 1
            if body:
                out.append(f"### 🤖 Reactie — {ts(e)}")
                out.append("")
                out.append(body)
                out.append("")
            for name, args in calls:
                n_tool += 1
                out.append(f"- ⚙️ **{name}** — {summarize_args(args)}")
            if calls:
                out.append("")
        elif role == "toolResult":
            # output van tools: kort meegeven (afgekapt)
            body = text_of(msg.get("content")).strip()
            if body:
                if len(body) > 600:
                    body = body[:600] + " … *(afgekapt)*"
                out.append(f"  > 📎 `{msg.get('toolName','tool')}`: {body.replace(chr(10), ' ')}")
                out.append("")

    out.append("---")
    out.append("")
    out.append(f"*{n_user} prompts · {n_asst} reacties · {n_tool} tool-acties — "
               f"volledige ruwe sessie staat naast dit bestand als `.jsonl`.*")
    out.append("")

    with open(dst, "w", encoding="utf-8") as f:
        f.write("\n".join(out))
    print(f"OK: {dst} ({n_user} prompts, {n_asst} reacties, {n_tool} tool-acties)")


if __name__ == "__main__":
    main()
