import { Archive, Bell, Bot, Server } from "lucide-react";

import { PageShell } from "@/components/page-shell";
import { SectionCard } from "@/components/section-card";
import { StatusBadge } from "@/components/status-badge";
import { Button } from "@/components/ui/button";
import { getBackendHealth } from "@/lib/api-client";
import { serviceStatuses } from "@/lib/mock-data";

export default async function DevOpsPage() {
  const health = await getBackendHealth();
  const statuses = serviceStatuses.map((service) =>
    service.name === "FastAPI Backend"
      ? {
          ...service,
          status: health.data?.status === "ok" ? "online" : "offline",
        }
      : service,
  );

  return (
    <PageShell
      title="系统运维"
      eyebrow="DevOps"
      description="聚合后端服务、编译 Worker、模型网关和存储服务状态。FastAPI Backend 状态复用 `/health`。"
    >
      <div className="grid gap-4 md:grid-cols-4">
        {statuses.map((service) => (
          <SectionCard key={service.name}>
            <div className="flex items-start justify-between gap-3">
              <Server className="size-8 text-blue-600" />
              <StatusBadge
                status={service.status}
                label={service.status === "online" ? "在线" : "离线"}
              />
            </div>
            <h2 className="mt-4 font-semibold text-zinc-950">{service.name}</h2>
            <div className="mt-3 h-2 rounded-full bg-zinc-100">
              <div
                className="h-2 rounded-full bg-blue-600"
                style={{ width: service.usage }}
              />
            </div>
            <p className="mt-2 text-xs text-zinc-500">
              资源使用率 {service.usage}
            </p>
          </SectionCard>
        ))}
      </div>

      <div className="grid gap-5 lg:grid-cols-3">
        <SectionCard
          title="监控告警"
          description="告警规则后续关联邮件/钉钉/飞书"
        >
          <div className="space-y-3">
            {[
              "队列长度超过 100",
              "LLM 错误率超过 5%",
              "磁盘使用率超过 80%",
            ].map((rule) => (
              <div
                key={rule}
                className="flex items-center justify-between rounded-xl bg-zinc-50 p-3"
              >
                <span className="inline-flex items-center gap-2 text-sm text-zinc-700">
                  <Bell className="size-4 text-amber-600" />
                  {rule}
                </span>
                <span className="text-xs text-blue-600">启用</span>
              </div>
            ))}
          </div>
        </SectionCard>

        <SectionCard title="LLM 模型池" description="主备切换与故障转移">
          <div className="space-y-3">
            {["DeepSeek V3 主模型", "Claude Sonnet 备用", "GPT 兼容接口"].map(
              (model, index) => (
                <div key={model} className="rounded-xl bg-zinc-50 p-3">
                  <div className="flex items-center gap-2 text-sm font-medium text-zinc-950">
                    <Bot className="size-4 text-blue-600" />
                    {model}
                  </div>
                  <p className="mt-1 text-xs text-zinc-500">
                    {index === 0 ? "当前主力模型" : "备用通道"}
                  </p>
                </div>
              ),
            )}
          </div>
        </SectionCard>

        <SectionCard
          title="备份恢复"
          description="备份 wiki/ 目录和数据库"
          actions={
            <Button variant="outline" size="sm">
              <Archive className="size-4" />
              立即备份
            </Button>
          }
        >
          <div className="rounded-2xl bg-zinc-50 p-4 text-sm leading-6 text-zinc-600">
            最近备份：2026-05-25 02:00
            <br />
            保留策略：每日增量，最近 30 天。
          </div>
        </SectionCard>
      </div>
    </PageShell>
  );
}
