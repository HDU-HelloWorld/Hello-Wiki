import { LockKeyhole, Sparkles, Wand2 } from "lucide-react";

import { InitTagsControl } from "@/components/init-tags-control";
import { PageShell } from "@/components/page-shell";
import { SectionCard } from "@/components/section-card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

const panels = [
  "基本设置",
  "CLAUDE.md",
  "AGENTS.md",
  "LLM 配置",
  "安全设置",
  "版本定价",
];

export default function SettingsPage() {
  return (
    <PageShell
      title="系统设置"
      eyebrow="Settings"
      description="配置系统基础信息、编译规则、问答规则、LLM 参数和安全策略。规则文件后续复用后端文件接口。"
      actions={<Button>保存配置</Button>}
    >
      <div className="grid gap-5 lg:grid-cols-[260px_1fr]">
        <SectionCard title="配置面板">
          <div className="space-y-2">
            {panels.map((panel, index) => (
              <button
                key={panel}
                className={`w-full rounded-xl px-3 py-2 text-left text-sm ${
                  index === 0
                    ? "bg-blue-50 font-medium text-blue-700"
                    : "text-zinc-600 hover:bg-zinc-50"
                }`}
                type="button"
              >
                {panel}
              </button>
            ))}
          </div>
        </SectionCard>

        <div className="space-y-5">
          <SectionCard
            title="基本设置"
            description="系统名称、Slogan 与功能开关"
          >
            <div className="grid gap-4 md:grid-cols-2">
              <label className="space-y-2">
                <span className="text-sm font-medium text-zinc-700">
                  系统名称
                </span>
                <Input defaultValue="知原" />
              </label>
              <label className="space-y-2">
                <span className="text-sm font-medium text-zinc-700">
                  Slogan
                </span>
                <Input defaultValue="让知识真正被理解，而非被检索" />
              </label>
            </div>
          </SectionCard>

          <InitTagsControl />

          <div className="grid gap-5 md:grid-cols-2">
            <SectionCard title="编译规则 CLAUDE.md">
              <div className="rounded-2xl bg-zinc-950 p-4 font-mono text-xs leading-6 text-zinc-100">
                # Wiki 目录结构
                <br />
                - 每个独立概念生成一个 Markdown 页面
                <br />- 使用 [[双链]] 连接相关知识点
              </div>
            </SectionCard>
            <SectionCard title="问答规则 AGENTS.md">
              <div className="rounded-2xl bg-zinc-950 p-4 font-mono text-xs leading-6 text-zinc-100">
                confidence_threshold: 0.3
                <br />
                context_turns: 10
                <br />
                cite_sources: true
              </div>
            </SectionCard>
          </div>

          <div className="grid gap-4 md:grid-cols-3">
            <SectionCard>
              <Sparkles className="size-8 text-blue-600" />
              <h3 className="mt-4 font-semibold text-zinc-950">LLM 配置</h3>
              <p className="mt-2 text-sm leading-6 text-zinc-500">
                主力模型、备用模型和温度参数。
              </p>
            </SectionCard>
            <SectionCard>
              <LockKeyhole className="size-8 text-blue-600" />
              <h3 className="mt-4 font-semibold text-zinc-950">安全设置</h3>
              <p className="mt-2 text-sm leading-6 text-zinc-500">
                IP 白名单、敏感词和 API 调用限制。
              </p>
            </SectionCard>
            <SectionCard>
              <Wand2 className="size-8 text-blue-600" />
              <h3 className="mt-4 font-semibold text-zinc-950">版本定价</h3>
              <p className="mt-2 text-sm leading-6 text-zinc-500">
                License 状态、功能权限和升级入口。
              </p>
            </SectionCard>
          </div>
        </div>
      </div>
    </PageShell>
  );
}
