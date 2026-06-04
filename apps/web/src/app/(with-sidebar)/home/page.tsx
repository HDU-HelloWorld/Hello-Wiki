import Link from "next/link";
import {
  BookOpen,
  Bot,
  FileCheck2,
  FileText,
  MessageSquare,
  Upload,
} from "lucide-react";

import { PageShell } from "@/components/page-shell";
import { SectionCard } from "@/components/section-card";
import { StatCard } from "@/components/stat-card";
import { StatusBadge } from "@/components/status-badge";
import { Button } from "@/components/ui/button";
import { conversations, dashboardStats, documents } from "@/lib/mock-data";
import { getBackendHealth, getWikiStats } from "@/lib/api-client";

const quickActions = [
  { href: "/knowledge", label: "上传文档", icon: Upload },
  { href: "/compile", label: "开始编译", icon: FileText },
  { href: "/chat", label: "智能对话", icon: MessageSquare },
  { href: "/wiki", label: "浏览 Wiki", icon: BookOpen },
  { href: "/audit", label: "知识审核", icon: FileCheck2 },
  { href: "/simulation", label: "模拟测试", icon: Bot },
];

export default async function HomePage() {
  const [health, wikiStats] = await Promise.all([
    getBackendHealth(),
    getWikiStats(),
  ]);
  const pageCount = wikiStats.data?.total_pages;
  const stats = dashboardStats.map((item) =>
    item.label === "Wiki 页面" && typeof pageCount === "number"
      ? { ...item, value: String(pageCount), hint: "来自 /api/v1/wiki/stats" }
      : item,
  );

  return (
    <PageShell
      title="工作台"
      eyebrow="Dashboard"
      description="聚合 Wiki 健康度、最近文档、最近对话和高频操作，作为客服和知识编辑的日常入口。"
      actions={
        <StatusBadge
          status={health.data?.status === "ok" ? "online" : "offline"}
          label={
            health.data?.status === "ok"
              ? "后端在线"
              : "后端未连接，显示样例数据"
          }
        />
      }
    >
      <section className="rounded-3xl bg-gradient-to-br from-blue-600 to-indigo-600 p-5 text-white shadow-lg">
        <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
          <div>
            <p className="text-sm text-blue-100">知原 v2.0 · 编译式 Wiki</p>
            <h2 className="mt-2 text-2xl font-semibold">
              知识输入到智能问答闭环运行中
            </h2>
            <p className="mt-2 max-w-2xl text-sm leading-6 text-blue-100">
              当前页面优先复用后端 `/health` 与
              `/api/v1/wiki/stats`，其他指标使用原型样例数据补齐。
            </p>
          </div>
          <Button asChild variant="secondary">
            <Link href="/knowledge">进入知识库</Link>
          </Button>
        </div>
        <div className="mt-5 grid gap-3 md:grid-cols-4">
          {stats.map((item) => (
            <StatCard
              key={item.label}
              label={item.label}
              value={item.value}
              hint={item.hint}
              tone={item.tone}
            />
          ))}
        </div>
      </section>

      <div className="grid gap-5 lg:grid-cols-[1.2fr_0.8fr]">
        <SectionCard title="最近文档" description="上传与编译状态概览">
          <div className="space-y-3">
            {documents.slice(0, 4).map((document) => (
              <div
                key={document.id}
                className="flex flex-col gap-3 rounded-xl border border-zinc-100 p-3 md:flex-row md:items-center md:justify-between"
              >
                <div>
                  <div className="font-medium text-zinc-950">
                    {document.name}
                  </div>
                  <div className="mt-1 text-xs text-zinc-500">
                    {document.owner} · 生成 {document.wikiPages} 个 Wiki 页面 ·{" "}
                    {document.uploadedAt}
                  </div>
                </div>
                <StatusBadge
                  status={document.status}
                  label={document.statusLabel}
                />
              </div>
            ))}
          </div>
        </SectionCard>

        <SectionCard title="最近对话" description="未知问题会沉淀到运营分析">
          <div className="space-y-3">
            {conversations.map((conversation) => (
              <div key={conversation.id} className="rounded-xl bg-zinc-50 p-3">
                <div className="flex items-start justify-between gap-3">
                  <p className="text-sm font-medium leading-6 text-zinc-950">
                    {conversation.question}
                  </p>
                  <StatusBadge
                    status={conversation.status}
                    label={conversation.statusLabel}
                  />
                </div>
                <p className="mt-2 text-xs text-zinc-500">
                  {conversation.time}
                </p>
              </div>
            ))}
          </div>
        </SectionCard>
      </div>

      <SectionCard title="快捷操作" description="对应原型中的 6 个零层级入口">
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-6">
          {quickActions.map((action) => {
            const Icon = action.icon;
            return (
              <Link
                key={action.href}
                href={action.href}
                className="flex flex-col gap-3 rounded-2xl border border-zinc-200 bg-white p-4 transition hover:-translate-y-0.5 hover:border-blue-200 hover:shadow-md"
              >
                <span className="flex size-10 items-center justify-center rounded-xl bg-blue-50 text-blue-600">
                  <Icon className="size-5" />
                </span>
                <span className="text-sm font-medium text-zinc-950">
                  {action.label}
                </span>
              </Link>
            );
          })}
        </div>
      </SectionCard>
    </PageShell>
  );
}
