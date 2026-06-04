"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { Play, RefreshCw } from "lucide-react";

import { DocumentUploadControl } from "@/components/document-upload-control";
import { MockTable, type MockTableColumn } from "@/components/mock-table";
import { SectionCard } from "@/components/section-card";
import { StatusBadge } from "@/components/status-badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  compileIngestDocument,
  getIngestStatus,
  listIngestDocuments,
  type IngestDocumentItem,
} from "@/lib/api-client";

const STATUS_LABELS: Record<string, string> = {
  pending: "待编译",
  compiling: "编译中",
  compiled: "已编译",
  partial: "部分成功",
  failed: "失败",
};

function formatUploadedAt(value: string) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  return date.toLocaleString("zh-CN", {
    month: "numeric",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function KnowledgeWorkspace() {
  const [documents, setDocuments] = useState<IngestDocumentItem[]>([]);
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("全部");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [compilingIds, setCompilingIds] = useState<Set<string>>(new Set());

  const refreshDocuments = useCallback(async () => {
    setError(null);
    const result = await listIngestDocuments();
    if (result.error || !result.data) {
      setError(result.error ?? "加载文档列表失败");
      return;
    }
    setDocuments(result.data.items);
  }, []);

  useEffect(() => {
    let cancelled = false;

    async function loadInitialDocuments() {
      setLoading(true);
      const result = await listIngestDocuments();
      if (cancelled) {
        return;
      }
      if (result.error || !result.data) {
        setError(result.error ?? "加载文档列表失败");
      } else {
        setDocuments(result.data.items);
      }
      setLoading(false);
    }

    void loadInitialDocuments();

    return () => {
      cancelled = true;
    };
  }, []);

  async function pollCompileTask(documentId: string, taskId: string) {
    for (let attempt = 0; attempt < 40; attempt += 1) {
      const result = await getIngestStatus(taskId);
      if (
        result.data &&
        (result.data.status === "completed" ||
          result.data.status === "failed" ||
          result.data.status === "partial")
      ) {
        break;
      }
      await new Promise((resolve) => setTimeout(resolve, 1500));
    }
    setCompilingIds((current) => {
      const next = new Set(current);
      next.delete(documentId);
      return next;
    });
    await refreshDocuments();
  }

  async function startCompile(documentId: string) {
    setCompilingIds((current) => new Set(current).add(documentId));
    setError(null);

    const result = await compileIngestDocument(documentId);
    if (result.error || !result.data) {
      setCompilingIds((current) => {
        const next = new Set(current);
        next.delete(documentId);
        return next;
      });
      setError(result.error ?? "启动编译失败");
      return;
    }

    await pollCompileTask(documentId, result.data.task_id);
  }

  const filteredDocuments = useMemo(() => {
    return documents.filter((document) => {
      const matchesSearch =
        search.trim() === "" ||
        document.filename.toLowerCase().includes(search.trim().toLowerCase());
      const matchesStatus =
        statusFilter === "全部" ||
        STATUS_LABELS[document.status] === statusFilter ||
        document.status === statusFilter;
      return matchesSearch && matchesStatus;
    });
  }, [documents, search, statusFilter]);

  const columns: MockTableColumn<IngestDocumentItem>[] = [
    {
      key: "name",
      header: "文档",
      render: (row) => (
        <div>
          <div className="font-medium text-zinc-950">{row.filename}</div>
          <div className="mt-1 text-xs text-zinc-500">{row.domain}</div>
        </div>
      ),
    },
    {
      key: "status",
      header: "编译状态",
      render: (row) => (
        <StatusBadge
          status={row.status}
          label={STATUS_LABELS[row.status] ?? row.status}
        />
      ),
    },
    {
      key: "pages",
      header: "Wiki 页面",
      render: (row) => `${row.wiki_pages} 个`,
    },
    {
      key: "time",
      header: "上传时间",
      render: (row) => formatUploadedAt(row.uploaded_at),
    },
    {
      key: "action",
      header: "操作",
      render: (row) => {
        const isCompiling =
          compilingIds.has(row.document_id) || row.status === "compiling";
        const canCompile =
          row.status === "pending" ||
          row.status === "failed" ||
          row.status === "partial";

        return (
          <Button
            variant="ghost"
            size="sm"
            disabled={!canCompile || isCompiling}
            onClick={() => void startCompile(row.document_id)}
          >
            <Play className="size-4" />
            {isCompiling ? "编译中…" : "开始编译"}
          </Button>
        );
      },
    },
  ];

  return (
    <>
      <SectionCard>
        <DocumentUploadControl
          onUploaded={async () => {
            setLoading(true);
            await refreshDocuments();
            setLoading(false);
          }}
        />
      </SectionCard>

      <SectionCard>
        <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
          <Input
            className="lg:max-w-md"
            placeholder="按文件名搜索"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
          />
          <div className="flex flex-wrap gap-2">
            {["全部", "待编译", "编译中", "已编译", "失败"].map((item) => (
              <Button
                key={item}
                variant={statusFilter === item ? "default" : "outline"}
                size="sm"
                onClick={() => setStatusFilter(item)}
              >
                {item}
              </Button>
            ))}
            <Button
              variant="outline"
              size="sm"
              onClick={() => {
                setLoading(true);
                void refreshDocuments().finally(() => setLoading(false));
              }}
            >
              <RefreshCw className="size-4" />
              刷新
            </Button>
          </div>
        </div>
      </SectionCard>

      <SectionCard
        title="文档列表"
        description="上传后默认进入待编译队列；点击「开始编译」才会触发 ingest 流水线。"
      >
        {error ? <p className="mb-3 text-sm text-red-600">{error}</p> : null}
        {loading ? (
          <p className="text-sm text-zinc-500">加载中…</p>
        ) : (
          <MockTable
            rows={filteredDocuments}
            columns={columns}
            getRowKey={(row) => row.document_id}
            emptyText="暂无文档，请先上传文件"
          />
        )}
        {filteredDocuments.some((row) => row.error) ? (
          <div className="mt-3 space-y-1 text-xs text-red-600">
            {filteredDocuments
              .filter((row) => row.error)
              .map((row) => (
                <p key={row.document_id}>
                  {row.filename}：{row.error}
                </p>
              ))}
          </div>
        ) : null}
      </SectionCard>
    </>
  );
}
