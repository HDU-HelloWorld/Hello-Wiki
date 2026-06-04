import { Download, Upload } from "lucide-react";

import { KnowledgeWorkspace } from "@/components/knowledge-workspace";
import { PageShell } from "@/components/page-shell";
import { SectionCard } from "@/components/section-card";
import { Button } from "@/components/ui/button";
import { wikiPages } from "@/lib/mock-data";
import { getWikiPages } from "@/lib/api-client";

export default async function KnowledgePage() {
  const wikiResponse = await getWikiPages();
  const realWikiPages = wikiResponse.data?.items ?? [];

  return (
    <PageShell
      title="知识库"
      eyebrow="Knowledge"
      description="管理原始文档、编译状态和 Wiki 产物。上传后进入待编译队列，由你在列表中确认后再开始编译。"
      actions={
        <>
          <Button variant="outline">
            <Download className="size-4" />
            导出 Wiki
          </Button>
          <Button variant="outline" disabled>
            <Upload className="size-4" />
            在下方上传
          </Button>
        </>
      }
    >
      <KnowledgeWorkspace />

      <SectionCard
        title="编译产物预览"
        description="来自真实 Wiki API 或本地样例数据"
      >
        <div className="grid gap-3 md:grid-cols-3">
          {(realWikiPages.length > 0 ? realWikiPages : wikiPages).map(
            (page) => (
              <article
                key={page.id}
                className="rounded-2xl border border-zinc-200 bg-zinc-50 p-4"
              >
                <h3 className="font-semibold text-zinc-950">{page.title}</h3>
                <p className="mt-2 line-clamp-3 text-sm leading-6 text-zinc-500">
                  {"summary" in page ? page.summary : page.content}
                </p>
                <div className="mt-3 flex flex-wrap gap-1.5">
                  {page.tags.map((tag) => (
                    <span
                      key={tag}
                      className="rounded-full bg-blue-50 px-2 py-0.5 text-xs text-blue-700"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              </article>
            ),
          )}
        </div>
      </SectionCard>
    </PageShell>
  );
}
