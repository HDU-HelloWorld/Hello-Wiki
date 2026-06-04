import { FileText } from "lucide-react";

import { AgentChatConsole } from "@/components/agent-chat-console";
import { PageShell } from "@/components/page-shell";
import { SectionCard } from "@/components/section-card";
import { StatusBadge } from "@/components/status-badge";
import { wikiPages } from "@/lib/mock-data";

export default function ChatPage() {
  return (
    <PageShell
      title="智能对话"
      eyebrow="Chat"
      description="三栏结构模拟客服问答：左侧 Wiki 覆盖范围，中间多轮对话，右侧展示本轮引用来源。对话直接调用 TS agent-ai，由 TS 使用 JSONL 管理会话记忆。"
      actions={<StatusBadge status="online" label="直连 TS Agent API" />}
    >
      <div className="grid min-h-[720px] gap-5 xl:grid-cols-[280px_1fr_320px]">
        <SectionCard title="Wiki 导航" description="辅助客服判断知识覆盖范围">
          <div className="space-y-2">
            {wikiPages.map((page) => (
              <div key={page.id} className="rounded-xl bg-zinc-50 p-3">
                <div className="flex items-center gap-2 text-sm font-medium text-zinc-950">
                  <FileText className="size-4 text-blue-600" />
                  {page.title}
                </div>
                <p className="mt-1 line-clamp-2 text-xs leading-5 text-zinc-500">
                  {page.summary}
                </p>
              </div>
            ))}
          </div>
        </SectionCard>

        <SectionCard className="flex flex-col" title="对话区">
          <AgentChatConsole />
        </SectionCard>

        <SectionCard
          title="引用上下文"
          description="展示本轮回答引用的 Wiki 页面"
        >
          <div className="space-y-3">
            {wikiPages.slice(0, 2).map((page) => (
              <article
                key={page.id}
                className="rounded-2xl border border-zinc-200 bg-white p-4"
              >
                <h3 className="font-medium text-zinc-950">{page.title}</h3>
                <p className="mt-2 text-sm leading-6 text-zinc-500">
                  {page.summary}
                </p>
                <div className="mt-3 flex flex-wrap gap-1.5">
                  {page.tags.map((tag) => (
                    <span
                      key={tag}
                      className="rounded-full bg-zinc-100 px-2 py-0.5 text-xs text-zinc-600"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              </article>
            ))}
          </div>
        </SectionCard>
      </div>
    </PageShell>
  );
}
