import { Download, TrendingUp } from "lucide-react";

import { MockTable, type MockTableColumn } from "@/components/mock-table";
import { PageShell } from "@/components/page-shell";
import { SectionCard } from "@/components/section-card";
import { StatCard } from "@/components/stat-card";
import { StatusBadge } from "@/components/status-badge";
import { Button } from "@/components/ui/button";
import { dialogLogs, unresolvedQuestions } from "@/lib/mock-data";

type DialogRow = (typeof dialogLogs)[number];

const dialogColumns: MockTableColumn<DialogRow>[] = [
  { key: "user", header: "用户", render: (row) => row.user },
  { key: "question", header: "问题", render: (row) => row.question },
  {
    key: "result",
    header: "状态",
    render: (row) => (
      <StatusBadge
        status={row.result === "未知" ? "unknown" : "answered"}
        label={row.result}
      />
    ),
  },
  { key: "score", header: "反馈", render: (row) => row.score },
];

export default function OpsPage() {
  return (
    <PageShell
      title="运营后台"
      eyebrow="Analytics"
      description="对话质量、知识覆盖率和未知问题的运营驾驶舱。当前以原型样例展示，后续接 `/api/analytics/*` 和对话日志分页接口。"
      actions={
        <Button variant="outline">
          <Download className="size-4" />
          导出报表
        </Button>
      }
    >
      <div className="grid gap-4 md:grid-cols-4">
        <StatCard label="今日对话" value="342" hint="峰值 14:00" tone="blue" />
        <StatCard
          label="知识覆盖率"
          value="87%"
          hint="未知问题 43 条"
          tone="green"
        />
        <StatCard
          label="满意度"
          value="92%"
          hint="按用户反馈统计"
          tone="amber"
        />
        <StatCard label="待补知识" value="17" hint="高频问题聚合" tone="red" />
      </div>

      <SectionCard
        title="总览趋势"
        description="图表库后续可接 ECharts 或 Chart.js"
      >
        <div className="grid gap-3 md:grid-cols-7">
          {[42, 58, 49, 72, 86, 63, 91].map((value, index) => (
            <div
              key={index}
              className="flex h-48 flex-col justify-end rounded-2xl bg-zinc-50 p-3"
            >
              <div
                className="rounded-t-xl bg-blue-500"
                style={{ height: `${value}%` }}
              />
              <div className="mt-2 text-center text-xs text-zinc-500">
                D-{6 - index}
              </div>
            </div>
          ))}
        </div>
      </SectionCard>

      <div className="grid gap-5 lg:grid-cols-[1.1fr_0.9fr]">
        <SectionCard title="对话日志" description="生产环境需要后端分页">
          <MockTable
            rows={dialogLogs}
            columns={dialogColumns}
            getRowKey={(row) => row.id}
          />
        </SectionCard>

        <SectionCard
          title="知识分析"
          description="未知问题按频次排序，推动知识库补充"
          actions={<TrendingUp className="size-5 text-blue-600" />}
        >
          <div className="space-y-3">
            {unresolvedQuestions.map((item) => (
              <div key={item.question} className="rounded-2xl bg-zinc-50 p-4">
                <div className="flex items-start justify-between gap-3">
                  <p className="text-sm font-medium leading-6 text-zinc-950">
                    {item.question}
                  </p>
                  <span className="rounded-full bg-red-50 px-2 py-0.5 text-xs font-medium text-red-700">
                    {item.count} 次
                  </span>
                </div>
                <p className="mt-2 text-xs text-zinc-500">
                  建议责任部门：{item.owner}
                </p>
              </div>
            ))}
          </div>
        </SectionCard>
      </div>
    </PageShell>
  );
}
