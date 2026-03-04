# agent.py — Updated for Groq SDK + dotenv
import os
import json
import sys
from lsp_client import LSPClient
from dotenv import load_dotenv
from groq import Groq

# ─── Load .env file ───────────────────────────────────────────────────────────
load_dotenv()

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

# ─── Groq client ─────────────────────────────────────────────────────────────
client = Groq(api_key=GROQ_API_KEY)

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_diagnostics",
            "description": "Get all errors, warnings, and issues in the file using the language server.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "hover",
            "description": "Get type information and documentation for a symbol at a specific line and character position.",
            "parameters": {
                "type": "object",
                "properties": {
                    "line": {"type": "integer", "description": "Line number (1-indexed)"},
                    "character": {"type": "integer", "description": "Character/column position"}
                },
                "required": ["line", "character"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_completions",
            "description": "Get autocomplete suggestions at a specific position in the file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "line": {"type": "integer"},
                    "character": {"type": "integer"}
                },
                "required": ["line", "character"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "go_to_definition",
            "description": "Find where a symbol (function, class, variable) is defined.",
            "parameters": {
                "type": "object",
                "properties": {
                    "line": {"type": "integer"},
                    "character": {"type": "integer"}
                },
                "required": ["line", "character"]
            }
        }
    },
]


def call_lsp_tool(lsp: LSPClient, tool_name: str, tool_input: dict) -> str:
    """Execute the LSP tool the model chose and return result as string."""

    if tool_name == "get_diagnostics":
        results = lsp.get_diagnostics()
        if not results:
            return "No diagnostics found — file looks clean!"
        formatted = []
        for d in results:
            line = d.get("range", {}).get("start", {}).get("line", 0) + 1
            msg = d.get("message", "")
            severity = {1: "ERROR", 2: "WARNING", 3: "INFO"}.get(d.get("severity", 3), "INFO")
            formatted.append(f"Line {line} [{severity}]: {msg}")
        return "\n".join(formatted)

    elif tool_name == "hover":
        return lsp.hover(tool_input["line"], tool_input["character"])

    elif tool_name == "get_completions":
        completions = lsp.get_completions(tool_input["line"], tool_input["character"])
        return "Completions: " + ", ".join(completions) if completions else "No completions found."

    elif tool_name == "go_to_definition":
        result = lsp.go_to_definition(tool_input["line"], tool_input["character"])
        if result:
            return f"Defined at line {result['line']} in {result['file']}"
        return "Definition not found."

    return "Unknown tool."


def ask_agent(lsp: LSPClient, user_question: str, file_content: str):
    """Agentic loop — model calls LSP tools until it has a final answer."""

    system_prompt = f"""You are a code analysis agent. You have access to a Language Server Protocol (LSP) 
client that can analyze Python code. Use the tools to answer the user's question accurately. don't analyze the code by yourself strictly

Here is the Python file being analyzed:
```python
{file_content}
```

When the user asks about errors, types, definitions, or completions — use the appropriate LSP tool.
After getting the LSP result, explain it clearly in plain English."""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_question}
    ]

    # ─── Agentic loop ─────────────────────────────────────────────────────────
    while True:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=3000,
            tools=TOOLS,
            messages=messages,
        )

        message = response.choices[0].message
        finish_reason = response.choices[0].finish_reason

        # Append assistant message to history
        # Convert to dict because Groq SDK returns objects, not plain dicts
        messages.append({
            "role": "assistant",
            "content": message.content or "",
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    }
                }
                for tc in (message.tool_calls or [])
            ] or None
        })

        # ── Model wants to call a tool ─────────────────────────────────────────
        if finish_reason == "tool_calls":
            for tool_call in message.tool_calls:
                tool_name  = tool_call.function.name
                tool_input = json.loads(tool_call.function.arguments)  # SDK gives string, parse it

                print(f"\n  🔧 Calling LSP: {tool_name}({tool_input})")

                lsp_result = call_lsp_tool(lsp, tool_name, tool_input)

                print(f"  📡 LSP result: {lsp_result}")

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": lsp_result,
                })

        # ── Model gave final answer ────────────────────────────────────────────
        elif finish_reason == "stop":
            print(f"\n🤖 Agent: {message.content}")
            break


# ─── Entry point ──────────────────────────────────────────────────────────────
if __name__ == "__main__":

    # ── Check API key ──────────────────────────────────────────────────────────
    if not GROQ_API_KEY:
        print("❌ GROQ_API_KEY is not set.")
        print("   Add it to your .env file: GROQ_API_KEY=your-key-here")
        sys.exit(1)

    # ── Find the file to analyze ───────────────────────────────────────────────
    # Usage: python agent.py           → uses sample_code.py
    #        python agent.py myfile.py → analyzes any file you want
    if len(sys.argv) > 1:
        file_path = os.path.abspath(sys.argv[1])
    else:
        file_path = os.path.join(os.path.dirname(__file__), "sample_code.py")

    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        sys.exit(1)

    # ── Start the language server ──────────────────────────────────────────────
    print(f"\n🚀 Starting language server for: {file_path}")
    print("   (Takes ~2 seconds while pylsp indexes your file...)\n")

    lsp = LSPClient(file_path)

    with open(file_path, "r") as f:
        file_content = f.read()

    # ── Welcome banner ─────────────────────────────────────────────────────────
    print("✅ Ready!\n")
    print("─" * 55)
    print(f"  📂 File : {file_path}")
    print(f"  🤖 Model: llama-3.3-70b-versatile (Groq)")
    print("─" * 55)
    print("  Try asking:")
    print("    • What errors exist in this file?")
    print("    • What does the divide() function do?")
    print("    • Where is Calculator defined?")
    print("    • What can I type after 'self.' on line 28?")
    print("  Type 'quit' to exit.")
    print("─" * 55)

    # ── Chat loop ──────────────────────────────────────────────────────────────
    try:
        while True:
            try:
                user_input = input("\n💬 You: ").strip()
            except EOFError:
                break

            if not user_input:
                continue

            if user_input.lower() in ("quit", "exit", "q"):
                break

            ask_agent(lsp, user_input, file_content)

    finally:
        print("\n👋 Shutting down language server...")
        lsp.shutdown()
        print("Done. Bye!")