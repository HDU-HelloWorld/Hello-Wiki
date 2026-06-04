import { Copy, Globe2, KeyRound, MessageCircle } from "lucide-react";

import { PageShell } from "@/components/page-shell";
import { SectionCard } from "@/components/section-card";
import { StatusBadge } from "@/components/status-badge";
import { Button } from "@/components/ui/button";
import { channelCards } from "@/lib/mock-data";

const channelIcons = [Globe2, MessageCircle, KeyRound];

export default function ChannelsPage() {
  return (
    <PageShell
      title="多渠道接入"
      eyebrow="Channels"
      description="将同一套 Wiki 问答能力分发到官网、公众号、小程序和第三方系统。"
    >
      <div className="grid gap-4 md:grid-cols-3">
        {channelCards.map((channel, index) => {
          const Icon = channelIcons[index] ?? Globe2;
          return (
            <SectionCard key={channel.title}>
              <div className="flex items-start justify-between gap-3">
                <span className="flex size-11 items-center justify-center rounded-2xl bg-blue-50 text-blue-600">
                  <Icon className="size-5" />
                </span>
                <StatusBadge
                  status={channel.status}
                  label={channel.status === "online" ? "已启用" : "待配置"}
                />
              </div>
              <h2 className="mt-4 text-lg font-semibold text-zinc-950">
                {channel.title}
              </h2>
              <p className="mt-2 text-sm leading-6 text-zinc-500">
                {channel.detail}
              </p>
            </SectionCard>
          );
        })}
      </div>

      <SectionCard
        title="网站嵌入代码"
        description="复制到官网 HTML 底部即可出现客服浮窗。"
        actions={
          <Button variant="outline" size="sm">
            <Copy className="size-4" />
            复制代码
          </Button>
        }
      >
        <pre className="overflow-x-auto rounded-2xl bg-zinc-950 p-4 text-sm text-zinc-100">
          {`<script
  src="https://cdn.zhiyuan.ai/widget.js"
  data-workspace="default"
  data-title="知原智能客服"
></script>`}
        </pre>
      </SectionCard>
    </PageShell>
  );
}
