"use client";

import { useState } from "react";
import { Tags } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { initTags, type InitTagsResponse } from "@/lib/api-client";

export function InitTagsControl() {
  const [domain, setDomain] = useState("general");
  const [description, setDescription] = useState(
    "高校招生、奖学金、宿舍与校园服务知识库",
  );
  const [result, setResult] = useState<InitTagsResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  async function submit() {
    if (pending) return;
    setPending(true);
    setError(null);
    setResult(null);

    const response = await initTags({ domain, description, language: "zh" });
    if (response.error || !response.data) {
      setError(response.error ?? "初始化失败");
    } else {
      setResult(response.data);
    }
    setPending(false);
  }

  return (
    <div className="rounded-2xl border border-zinc-200 bg-white p-4">
      <div className="flex items-center gap-2 text-sm font-semibold text-zinc-950">
        <Tags className="size-4 text-blue-600" />
        标签体系初始化
      </div>
      <p className="mt-2 text-sm leading-6 text-zinc-500">
        调用 Python 固定工作流 `/api/v1/init/tags`，其中 LLM 子步骤由 TS
        ingest-ai 执行。 也可在 Chat 中让 Agent 调用 `init_tags` tool。
      </p>
      <div className="mt-4 grid gap-3 md:grid-cols-[180px_1fr_auto]">
        <Input
          value={domain}
          onChange={(event) => setDomain(event.target.value)}
        />
        <Input
          value={description}
          onChange={(event) => setDescription(event.target.value)}
        />
        <Button disabled={pending} onClick={() => void submit()}>
          {pending ? "初始化中" : "初始化标签"}
        </Button>
      </div>
      {result ? (
        <p className="mt-3 text-sm text-emerald-700">
          已生成 {result.categories} 个分类、{result.leaves} 个叶子标签。
        </p>
      ) : null}
      {error ? <p className="mt-3 text-sm text-red-600">{error}</p> : null}
    </div>
  );
}
