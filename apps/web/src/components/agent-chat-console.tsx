"use client";

import { useMemo, useState } from "react";
import { Bot, Send, UserRound } from "lucide-react";

import { StatusBadge } from "@/components/status-badge";
import { Button } from "@/components/ui/button";
import { postAgentChat } from "@/lib/agent-api-client";

type ChatMessage = {
  role: "user" | "assistant";
  content: string;
  status?: "unknown";
};

const initialMessages: ChatMessage[] = [
  {
    role: "assistant",
    content:
      "你好，我是知原 Agent。当前对话会直接发送到 TS agent-ai，并由 TS 使用 JSONL 管理会话记忆。",
  },
];

export function AgentChatConsole() {
  const [messages, setMessages] = useState<ChatMessage[]>(initialMessages);
  const [input, setInput] = useState("");
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const sessionId = useMemo(() => `web-${crypto.randomUUID()}`, []);

  async function submit() {
    const message = input.trim();
    if (!message || pending) return;

    setInput("");
    setError(null);
    setPending(true);
    setMessages((current) => [...current, { role: "user", content: message }]);

    try {
      const response = await postAgentChat({ message, sessionId });
      setMessages((current) => [
        ...current,
        { role: "assistant", content: response.reply },
      ]);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Agent 请求失败");
    } finally {
      setPending(false);
    }
  }

  return (
    <div className="flex h-full flex-col">
      <div className="flex min-h-[520px] flex-1 flex-col gap-4 rounded-2xl bg-zinc-50 p-4">
        <div className="rounded-xl border border-blue-100 bg-blue-50 px-3 py-2 text-xs leading-5 text-blue-800">
          可直接询问 Agent，例如：“请为高校招生知识库初始化标签体系，domain 用
          university_policy”。Agent 会调用 TS 侧 init_tags tool，再由 tool 调
          Python 固定工作流。
        </div>
        {messages.map((message, index) => {
          const assistant = message.role === "assistant";
          return (
            <div
              key={`${message.role}-${index}`}
              className={`flex gap-3 ${assistant ? "" : "justify-end"}`}
            >
              {assistant ? (
                <span className="flex size-9 shrink-0 items-center justify-center rounded-full bg-blue-600 text-white">
                  <Bot className="size-4" />
                </span>
              ) : null}
              <div
                className={`max-w-[78%] rounded-2xl px-4 py-3 text-sm leading-6 ${
                  assistant
                    ? "bg-white text-zinc-700 shadow-sm"
                    : "bg-blue-600 text-white"
                }`}
              >
                <p>{message.content}</p>
                {message.status === "unknown" ? (
                  <StatusBadge
                    status="unknown"
                    label="未知问题已沉淀"
                    className="mt-3"
                  />
                ) : null}
              </div>
              {!assistant ? (
                <span className="flex size-9 shrink-0 items-center justify-center rounded-full bg-zinc-900 text-white">
                  <UserRound className="size-4" />
                </span>
              ) : null}
            </div>
          );
        })}
        {pending ? (
          <div className="text-sm text-zinc-500">Agent 正在思考...</div>
        ) : null}
      </div>
      {error ? (
        <div className="mt-3 rounded-xl border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
          {error}
        </div>
      ) : null}
      <div className="mt-4 flex gap-2 rounded-2xl border border-zinc-200 bg-white p-2">
        <input
          className="min-w-0 flex-1 bg-transparent px-3 text-sm outline-none"
          placeholder="输入问题，直接调用 TS agent-ai"
          value={input}
          onChange={(event) => setInput(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === "Enter") {
              event.preventDefault();
              void submit();
            }
          }}
        />
        <Button disabled={pending} onClick={() => void submit()}>
          <Send className="size-4" />
          发送
        </Button>
      </div>
      <p className="mt-2 text-xs text-zinc-500">sessionId: {sessionId}</p>
    </div>
  );
}
