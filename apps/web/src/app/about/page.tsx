import Link from "next/link";

import { SectionCard } from "@/components/section-card";
import { Button } from "@/components/ui/button";

const loop = [
  "知识输入",
  "AI 编译",
  "Wiki 构建",
  "智能对话",
  "未知提醒",
  "持续优化",
];

export default function AboutPage() {
  return (
    <main className="min-h-dvh bg-[#F6F7FB] px-6 py-10">
      <div className="mx-auto flex max-w-5xl flex-col gap-6">
        <header className="rounded-3xl bg-white p-8 shadow-sm">
          <p className="text-sm font-semibold tracking-[0.2em] text-blue-600 uppercase">
            About ZhiYuan
          </p>
          <h1 className="mt-3 text-3xl font-semibold tracking-tight text-zinc-950">
            知原（ZhiYuan）编译式 Wiki 智能客服系统
          </h1>
          <p className="mt-4 max-w-3xl text-sm leading-7 text-zinc-500">
            系统将原始 PDF、Word、Markdown、TXT 文档经过 AI 编译后构建成结构化
            Wiki， 再通过智能问答提供精准、可靠、可溯源的客服回答。
          </p>
          <Button asChild className="mt-6">
            <Link href="/home">返回工作台</Link>
          </Button>
        </header>

        <SectionCard title="产品闭环">
          <div className="grid gap-3 md:grid-cols-6">
            {loop.map((item, index) => (
              <div
                key={item}
                className="rounded-2xl bg-blue-50 p-4 text-center"
              >
                <div className="mx-auto flex size-8 items-center justify-center rounded-full bg-blue-600 text-sm font-semibold text-white">
                  {index + 1}
                </div>
                <div className="mt-3 text-sm font-medium text-blue-950">
                  {item}
                </div>
              </div>
            ))}
          </div>
        </SectionCard>
      </div>
    </main>
  );
}
