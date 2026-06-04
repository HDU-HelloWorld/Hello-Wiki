"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import type { ReactNode } from "react";
import { Star } from "lucide-react";

import { Button } from "@/components/ui/button";
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarRail,
} from "@/components/ui/sidebar";
import { TooltipProvider } from "@/components/ui/tooltip";

type NavItem = {
  href: string;
  label: string;
  icon: ReactNode;
};

type NavGroup = {
  title: string;
  items: NavItem[];
};

const ICON_STROKE = 1.5;

function iconSvgProps() {
  return {
    className: "size-4 shrink-0",
    viewBox: "0 0 24 24",
    fill: "none" as const,
    stroke: "currentColor",
    strokeWidth: ICON_STROKE,
    strokeLinecap: "round" as const,
    strokeLinejoin: "round" as const,
    "aria-hidden": true as const,
  };
}

function WorkbenchIcon() {
  return (
    <svg {...iconSvgProps()}>
      <path d="M3 10.5L12 3l9 7.5V20a1 1 0 0 1-1 1h-5v-6H9v6H4a1 1 0 0 1-1-1v-9.5z" />
    </svg>
  );
}

function KnowledgeBaseIcon() {
  return (
    <svg {...iconSvgProps()}>
      <path d="M4 19V5c0-.5.5-1 1-1h6v15H5c-.5 0-1-.5-1-1z" />
      <path d="M13 19V4h6c.5 0 1 .5 1 1v14" />
      <path d="M8 8h3M8 11h3M16 8h3M16 11h3" />
    </svg>
  );
}

function ChatIcon() {
  return (
    <svg {...iconSvgProps()}>
      <path d="M4 6a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v6a2 2 0 0 1-2 2h-6l-4 3v-3H6a2 2 0 0 1-2-2V6z" />
      <circle cx="9" cy="9" r="1" />
      <circle cx="12" cy="9" r="1" />
      <circle cx="15" cy="9" r="1" />
    </svg>
  );
}

function WikiBrowseIcon() {
  return (
    <svg {...iconSvgProps()}>
      <path d="M4 6c0-1 .8-2 2-2h6v14H6c-1 0-2-.8-2-2V6z" />
      <path d="M14 6c0-1 .8-2 2-2h6v14h-6c-1 0-2-.8-2-2V6z" />
      <path d="M7 9h4M7 12h4M17 9h3M17 12h3" />
    </svg>
  );
}

function OpsIcon() {
  return (
    <svg {...iconSvgProps()}>
      <path d="M4 20V12M10 20V8M16 20v-6M22 20V4" />
    </svg>
  );
}

function AuditIcon() {
  return (
    <svg {...iconSvgProps()}>
      <rect x="5" y="3" width="14" height="18" rx="2" />
      <path d="M9 12l2 2 4-4" />
    </svg>
  );
}

function SimulationIcon() {
  return (
    <svg {...iconSvgProps()}>
      <rect x="7" y="8" width="10" height="10" rx="2" />
      <circle cx="10" cy="12" r="1" />
      <circle cx="14" cy="12" r="1" />
      <path d="M10 16h4" />
      <rect x="10.5" y="5" width="3" height="4" rx="0.5" />
    </svg>
  );
}

function ChannelsIcon() {
  return (
    <svg {...iconSvgProps()}>
      <path d="M9 17H7a5 5 0 0 1 0-10h2" />
      <path d="M15 7h2a5 5 0 0 1 0 10h-2" />
      <path d="M8 12h8" />
    </svg>
  );
}

function PermissionsIcon() {
  return (
    <svg {...iconSvgProps()}>
      <rect x="5" y="11" width="14" height="11" rx="2" />
      <path d="M8 11V7a4 4 0 0 1 8 0v4" />
      <circle cx="12" cy="16" r="1.5" />
    </svg>
  );
}

function DevOpsIcon() {
  return (
    <svg {...iconSvgProps()}>
      <path d="M14.7 6.3l1.4 1.4L6.9 17 5.5 15.6 14.7 6.3z" />
      <path d="M7 5L10 8L8.5 9.5L5.5 6.5L7 5z" />
    </svg>
  );
}

function SettingsIcon() {
  return (
    <svg {...iconSvgProps()}>
      <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09a1.65 1.65 0 0 0-1-1.51 1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09a1.65 1.65 0 0 0 1.51-1 1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82-.33V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z" />
    </svg>
  );
}

const NAV_GROUPS: NavGroup[] = [
  {
    title: "核心功能",
    items: [
      { href: "/home", label: "工作台", icon: <WorkbenchIcon /> },
      { href: "/knowledge", label: "知识库", icon: <KnowledgeBaseIcon /> },
      { href: "/chat", label: "智能对话", icon: <ChatIcon /> },
      { href: "/wiki", label: "Wiki 浏览", icon: <WikiBrowseIcon /> },
    ],
  },
  {
    title: "运营管理",
    items: [
      { href: "/ops", label: "运营后台", icon: <OpsIcon /> },
      { href: "/audit", label: "知识审核", icon: <AuditIcon /> },
      { href: "/simulation", label: "模拟测试", icon: <SimulationIcon /> },
    ],
  },
  {
    title: "系统",
    items: [
      { href: "/channels", label: "多渠道接入", icon: <ChannelsIcon /> },
      { href: "/permissions", label: "权限管理", icon: <PermissionsIcon /> },
      { href: "/devops", label: "系统运维", icon: <DevOpsIcon /> },
      { href: "/settings", label: "系统设置", icon: <SettingsIcon /> },
    ],
  },
];

function isActivePath(pathname: string, href: string) {
  if (pathname === href) return true;
  return pathname.startsWith(`${href}/`);
}

export default function SideBar() {
  const pathname = usePathname();

  return (
    <TooltipProvider>
      <Sidebar collapsible="icon">
        <SidebarHeader className="gap-3 border-b border-sidebar-border px-3 py-4">
          <div className="flex items-center gap-3 group-data-[collapsible=icon]:justify-center">
            <div className="flex size-11 shrink-0 items-center justify-center rounded-xl bg-[#2563EB] text-lg font-semibold text-white shadow-sm">
              知
            </div>
            <div className="min-w-0 leading-tight group-data-[collapsible=icon]:hidden">
              <div className="truncate text-[17px] font-semibold tracking-tight">
                知原
              </div>
              <div className="mt-0.5 truncate text-xs text-sidebar-foreground/60">
                v2.0 · 编译式 Wiki
              </div>
            </div>
          </div>
        </SidebarHeader>

        <SidebarContent className="gap-0 px-1 py-3">
          {NAV_GROUPS.map((group) => (
            <SidebarGroup key={group.title} className="p-0">
              <SidebarGroupLabel className="px-3 text-[11px] uppercase tracking-wider text-sidebar-foreground/50">
                {group.title}
              </SidebarGroupLabel>
              <SidebarGroupContent>
                <SidebarMenu>
                  {group.items.map((item) => {
                    const active = isActivePath(pathname, item.href);
                    return (
                      <SidebarMenuItem key={item.href}>
                        <SidebarMenuButton
                          asChild
                          isActive={active}
                          tooltip={item.label}
                          className="h-10 px-3"
                        >
                          <Link href={item.href}>
                            {item.icon}
                            <span>{item.label}</span>
                          </Link>
                        </SidebarMenuButton>
                      </SidebarMenuItem>
                    );
                  })}
                </SidebarMenu>
              </SidebarGroupContent>
            </SidebarGroup>
          ))}
        </SidebarContent>

        <SidebarFooter className="border-t border-sidebar-border">
          <div className="flex items-center gap-3 rounded-lg px-2 py-2 group-data-[collapsible=icon]:flex-col group-data-[collapsible=icon]:gap-2">
            <div
              className="flex size-10 shrink-0 items-center justify-center rounded-full bg-[#2563EB] text-sm font-medium text-white"
              aria-hidden
            >
              管
            </div>
            <div className="min-w-0 flex-1 leading-tight group-data-[collapsible=icon]:hidden">
              <div className="truncate text-sm font-semibold">管理员</div>
              <div className="truncate text-xs text-sidebar-foreground/60">
                企业版 · 管理员
              </div>
            </div>
            <Button
              type="button"
              variant="ghost"
              size="icon-sm"
              className="shrink-0 text-sidebar-foreground/60 hover:bg-sidebar-accent hover:text-sidebar-accent-foreground group-data-[collapsible=icon]:size-8"
              aria-label="账户菜单"
            >
              <Star className="size-4" />
            </Button>
          </div>
        </SidebarFooter>
        <SidebarRail />
      </Sidebar>
    </TooltipProvider>
  );
}
