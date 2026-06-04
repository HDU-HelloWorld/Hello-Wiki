import { Check, FileDiff, Pencil, X } from "lucide-react";

import { PageShell } from "@/components/page-shell";
import { SectionCard } from "@/components/section-card";
import { StatusBadge } from "@/components/status-badge";
import { Button } from "@/components/ui/button";
import { auditItems } from "@/lib/mock-data";

export default function AuditPage() {
  const active = auditItems[0];

  return (
    <PageShell
      title="知识审核"
      eyebrow="Review"
      description="人工复核编译产物，在 Wiki 内容正式生效前处理新增页面和冲突变更。"
    >
      <div className="grid gap-5 lg:grid-cols-[320px_1fr]">
        <SectionCard title="审核队列" description="侧边栏角标后续可接队列数量">
          <div className="space-y-3">
            {auditItems.map((item) => (
              <div
                key={item.id}
                className="rounded-2xl border border-zinc-200 bg-white p-4"
              >
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <h3 className="font-medium text-zinc-950">{item.title}</h3>
                    <p className="mt-1 text-xs text-zinc-500">
                      {item.owner} · {item.time}
                    </p>
                  </div>
                  <StatusBadge
                    status={item.type}
                    label={item.type === "conflict" ? "冲突" : "新增"}
                  />
                </div>
              </div>
            ))}
          </div>
        </SectionCard>

        <SectionCard
          title={`冲突对比：${active.title}`}
          description="红色区域为旧版本，绿色区域为新编译结果。"
          actions={
            <>
              <Button variant="outline" size="sm">
                <X className="size-4" />
                拒绝
              </Button>
              <Button variant="outline" size="sm">
                <Pencil className="size-4" />
                编辑后通过
              </Button>
              <Button size="sm">
                <Check className="size-4" />
                通过
              </Button>
            </>
          }
        >
          <div className="grid gap-4 md:grid-cols-2">
            <div className="rounded-2xl border border-red-100 bg-red-50 p-4">
              <div className="mb-3 flex items-center gap-2 text-sm font-semibold text-red-700">
                <FileDiff className="size-4" />
                旧版内容
              </div>
              <p className="text-sm leading-7 text-red-950">
                国家奖学金申请时间为每年 9 月，校级奖学金由学院自行安排。
              </p>
            </div>
            <div className="rounded-2xl border border-emerald-100 bg-emerald-50 p-4">
              <div className="mb-3 flex items-center gap-2 text-sm font-semibold text-emerald-700">
                <FileDiff className="size-4" />
                新版内容
              </div>
              <p className="text-sm leading-7 text-emerald-950">
                国家奖学金申请时间调整为每年 10
                月上旬，校级奖学金统一通过学生服务平台提交。
              </p>
            </div>
          </div>

          <div className="mt-5 rounded-2xl bg-zinc-50 p-4">
            <h3 className="text-sm font-semibold text-zinc-950">审核历史</h3>
            <div className="mt-3 space-y-2 text-sm text-zinc-600">
              <p>10:24 编译引擎检测到时间字段差异，自动标记冲突。</p>
              <p>10:26 知识编辑打开审核任务，等待人工确认。</p>
            </div>
          </div>
        </SectionCard>
      </div>
    </PageShell>
  );
}
