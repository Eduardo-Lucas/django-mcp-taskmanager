import json
import os
import anthropic
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from tasks.tools import TOOLS, execute_tool

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

SYSTEM = (
    "You are a task manager assistant. Use the available tools to help the user "
    "manage their tasks. Be concise and use markdown tables when listing tasks."
)


@login_required
def chat_page(request):
    return render(request, "tasks/chat.html")


@login_required
@csrf_exempt
def chat_api(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    data = json.loads(request.body)
    messages = data.get("messages", [])

    def stream():
        current_messages = list(messages)

        while True:
            with client.messages.stream(
                model="claude-sonnet-4-6",
                max_tokens=1024,
                system=SYSTEM,
                tools=TOOLS,
                messages=current_messages,
            ) as stream:
                full_response = stream.get_final_message()

            # Collect text from the response
            text_blocks = [b.text for b in full_response.content if b.type == "text"]
            tool_uses = [b for b in full_response.content if b.type == "tool_use"]

            if text_blocks:
                yield f"data: {json.dumps({'type': 'text', 'text': ''.join(text_blocks)})}\n\n"

            if not tool_uses or full_response.stop_reason != "tool_use":
                yield "data: [DONE]\n\n"
                break

            # Execute tools and continue
            current_messages.append({"role": "assistant", "content": full_response.content})
            tool_results = []
            for tool_use in tool_uses:
                try:
                    result = execute_tool(tool_use.name, tool_use.input)
                except Exception as e:
                    result = {"error": str(e)}
                yield f"data: {json.dumps({'type': 'tool', 'name': tool_use.name})}\n\n"
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": tool_use.id,
                    "content": json.dumps(result),
                })

            current_messages.append({"role": "user", "content": tool_results})

    return StreamingHttpResponse(stream(), content_type="text/event-stream")
