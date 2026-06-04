import { BookOpen, Clock, FileText, Search } from "lucide-react";

import { PageShell } from "@/components/page-shell";
import { SectionCard } from "@/components/section-card";
import { Input } from "@/components/ui/input";
import { getWikiPages, getWikiTree } from "@/lib/api-client";
import { wikiPages } from "@/lib/mock-data";

export default async function WikiBrowsePage() {
  const [pagesResponse, treeResponse] = await Promise.all([
    getWikiPages(),
    getWikiTree(),
  ]);
  const pages = pagesResponse.data?.items.length
    ? pagesResponse.data.items.map((page) => ({
        id: page.id,
        title: page.title,
        category: "真实 Wiki",
        tags: page.tags,
        updatedAt: new Date(page.updated_at).toLocaleString("zh-CN"),
        source: page.created_by ?? "Wiki API",
        summary: page.content.slice(0, 90),
        content: page.content,
      }))
    : wikiPages;
  const activePage = pages[0];

  return (
    <PageShell
      title="Wiki 浏览"
      eyebrow="Wiki"
      description="展示编译后的结构化知识页面。目录和页面内容优先读取 `/api/v1/wiki/tree` 与 `/api/v1/wiki/pages`。"
    >
      <div className="grid min-h-[680px] gap-5 lg:grid-cols-[320px_1fr]">
        <SectionCard title="目录树" description="支持后续接入展开状态记忆">
          <div className="relative mb-4">
            <Search className="pointer-events-none absolute top-2.5 left-3 size-4 text-zinc-400" />
            <Input className="pl-9" placeholder="搜索 Wiki 页面" />
          </div>
          <div className="space-y-2">
            {(treeResponse.data?.length ? treeResponse.data : []).length > 0 ? (
              treeResponse.data?.map((node) => (
                <div key={node.id} className="rounded-xl bg-zinc-50 p-3">
                  <div className="flex items-center gap-2 text-sm font-medium">
                    <BookOpen className="size-4 text-blue-600" />
                    {node.title}
                  </div>
                </div>
              ))
            ) : (
              <>
                {["招生政策", "学生资助", "校园服务"].map((category) => (
                  <div key={category} className="rounded-xl bg-zinc-50 p-3">
                    <div className="flex items-center gap-2 text-sm font-semibold text-zinc-950">
                      <BookOpen className="size-4 text-blue-600" />
                      {category}
                    </div>
                    <div className="mt-2 space-y-1 pl-6">
                      {wikiPages
                        .filter((page) => page.category === category)
                        .map((page) => (
                          <div
                            key={page.id}
                            className="rounded-lg px-2 py-1 text-sm text-zinc-600 hover:bg-white"
                          >
                            {page.title}
                          </div>
                        ))}
                    </div>
                  </div>
                ))}
              </>
            )}
          </div>
        </SectionCard>

        <SectionCard>
          <article className="mx-auto max-w-4xl">
            <div className="flex flex-wrap items-center gap-2">
              {activePage.tags.map((tag) => (
                <span
                  key={tag}
                  className="rounded-full bg-blue-50 px-2.5 py-1 text-xs font-medium text-blue-700"
                >
                  {tag}
                </span>
              ))}
            </div>
            <h2 className="mt-4 text-3xl font-semibold tracking-tight text-zinc-950">
              {activePage.title}
            </h2>
            <div className="mt-3 flex flex-wrap gap-4 text-sm text-zinc-500">
              <span className="inline-flex items-center gap-1.5">
                <Clock className="size-4" />
                {activePage.updatedAt}
              </span>
              <span className="inline-flex items-center gap-1.5">
                <FileText className="size-4" />
                来源：{activePage.source}
              </span>
            </div>
            <div className="mt-8 rounded-2xl border border-blue-100 bg-blue-50 p-4 text-sm leading-6 text-blue-900">
              {activePage.summary}
            </div>
            <div className="prose prose-zinc mt-8 max-w-none text-zinc-700">
              <p>{activePage.content}</p>
              <h3 className="mt-8 text-xl font-semibold text-zinc-950">
                关联页面
              </h3>
              <p>
                该页面在编译阶段会生成类似 [[奖学金政策]]
                的双链。当前基础页面先以文本展示， 后续接入 Markdown
                渲染与双链跳转。
              </p>
            </div>
          </article>
        </SectionCard>
      </div>
    </PageShell>
  );
}
