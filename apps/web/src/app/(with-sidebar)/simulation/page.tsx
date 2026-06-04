import { Download, PlayCircle, Upload } from "lucide-react";

import { MockTable, type MockTableColumn } from "@/components/mock-table";
import { PageShell } from "@/components/page-shell";
import { SectionCard } from "@/components/section-card";
import { StatCard } from "@/components/stat-card";
import { Button } from "@/components/ui/button";
import { simulationResults } from "@/lib/mock-data";

type SimulationRow = (typeof simulationResults)[number];

const columns: MockTableColumn<SimulationRow>[] = [
  { key: "scenario", header: "场景", render: (row) => row.scenario },
  { key: "accuracy", header: "准确率", render: (row) => row.accuracy },
  { key: "coverage", header: "完整度", render: (row) => row.coverage },
  { key: "consistency", header: "一致性", render: (row) => row.consistency },
];

export default function SimulationPage() {
  return (
    <PageShell
      title="模拟测试"
      eyebrow="Simulation"
      description="用预设题库评估问答准确率、完整度和一致性，沉淀知识缺口。"
      actions={
        <>
          <Button variant="outline">
            <Upload className="size-4" />
            导入题库
          </Button>
          <Button>
            <PlayCircle className="size-4" />
            运行测试
          </Button>
        </>
      }
    >
      <div className="grid gap-4 md:grid-cols-4">
        <StatCard label="测试题数" value="120" hint="3 个场景" tone="blue" />
        <StatCard
          label="平均准确率"
          value="88%"
          hint="较上次 +4%"
          tone="green"
        />
        <StatCard label="知识缺口" value="14" hint="需补充页面" tone="red" />
        <StatCard
          label="一致性"
          value="90%"
          hint="重复测试 3 次"
          tone="amber"
        />
      </div>

      <div className="grid gap-5 lg:grid-cols-[0.85fr_1.15fr]">
        <SectionCard title="场景选择" description="题库后续支持 JSON 导入导出">
          <div className="space-y-3">
            {simulationResults.map((item) => (
              <label
                key={item.id}
                className="flex cursor-pointer items-center gap-3 rounded-2xl border border-zinc-200 p-4"
              >
                <input
                  type="radio"
                  name="scenario"
                  defaultChecked={item.id === "s-1"}
                />
                <span className="font-medium text-zinc-950">
                  {item.scenario}
                </span>
              </label>
            ))}
          </div>
        </SectionCard>

        <SectionCard
          title="测试报告"
          description="摘要 + 逐题详情 + 知识缺口分析"
          actions={
            <Button variant="outline" size="sm">
              <Download className="size-4" />
              PDF 导出
            </Button>
          }
        >
          <MockTable
            rows={simulationResults}
            columns={columns}
            getRowKey={(row) => row.id}
          />
        </SectionCard>
      </div>
    </PageShell>
  );
}
