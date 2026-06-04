import { ShieldCheck, UserPlus, UsersRound } from "lucide-react";

import { MockTable, type MockTableColumn } from "@/components/mock-table";
import { PageShell } from "@/components/page-shell";
import { SectionCard } from "@/components/section-card";
import { StatusBadge } from "@/components/status-badge";
import { Button } from "@/components/ui/button";
import { members } from "@/lib/mock-data";

type MemberRow = (typeof members)[number];

const columns: MockTableColumn<MemberRow>[] = [
  { key: "name", header: "成员", render: (row) => row.name },
  { key: "role", header: "角色", render: (row) => row.role },
  { key: "team", header: "团队空间", render: (row) => row.team },
  {
    key: "status",
    header: "状态",
    render: (row) => (
      <StatusBadge
        status={row.status}
        label={row.status === "online" ? "在线" : "离线"}
      />
    ),
  },
];

export default function PermissionsPage() {
  return (
    <PageShell
      title="权限管理"
      eyebrow="Permissions"
      description="按成员、角色和团队空间组织 RBAC 权限。当前为前端基础界面，后续接认证与权限 API。"
      actions={
        <Button>
          <UserPlus className="size-4" />
          邀请成员
        </Button>
      }
    >
      <div className="grid gap-4 md:grid-cols-3">
        <SectionCard>
          <UsersRound className="size-8 text-blue-600" />
          <h2 className="mt-4 text-lg font-semibold text-zinc-950">成员管理</h2>
          <p className="mt-2 text-sm leading-6 text-zinc-500">
            用户 CRUD、邮件邀请与状态管理。
          </p>
        </SectionCard>
        <SectionCard>
          <ShieldCheck className="size-8 text-blue-600" />
          <h2 className="mt-4 text-lg font-semibold text-zinc-950">角色权限</h2>
          <p className="mt-2 text-sm leading-6 text-zinc-500">
            超级管理员、编辑、只读，以及企业版自定义角色。
          </p>
        </SectionCard>
        <SectionCard>
          <UsersRound className="size-8 text-blue-600" />
          <h2 className="mt-4 text-lg font-semibold text-zinc-950">团队空间</h2>
          <p className="mt-2 text-sm leading-6 text-zinc-500">
            多团队 Wiki 隔离，后端接口需带 workspace/team 过滤。
          </p>
        </SectionCard>
      </div>

      <SectionCard title="成员列表">
        <MockTable
          rows={members}
          columns={columns}
          getRowKey={(row) => row.id}
        />
      </SectionCard>
    </PageShell>
  );
}
