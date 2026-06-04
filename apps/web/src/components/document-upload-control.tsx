"use client";

import { useRef, useState } from "react";
import { FileUp, Upload } from "lucide-react";

import { Button } from "@/components/ui/button";
import { uploadIngestFile } from "@/lib/api-client";

type DocumentUploadControlProps = {
  domain?: string;
  onUploaded?: () => void | Promise<void>;
};

export function DocumentUploadControl({
  domain = "university_policy",
  onUploaded,
}: DocumentUploadControlProps) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [file, setFile] = useState<File | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [pending, setPending] = useState(false);

  async function upload() {
    if (!file || pending) return;
    setPending(true);
    setError(null);
    setMessage(null);

    const result = await uploadIngestFile({ file, domain });
    if (result.error || !result.data) {
      setError(result.error ?? "上传失败");
      setPending(false);
      return;
    }

    setMessage(`已加入待编译队列：${result.data.filename}`);
    setFile(null);
    if (inputRef.current) {
      inputRef.current.value = "";
    }
    await onUploaded?.();
    setPending(false);
  }

  return (
    <div className="rounded-2xl border border-dashed border-blue-200 bg-blue-50/60 p-4">
      <p className="mb-3 text-sm text-zinc-600">
        上传后文档进入待编译队列，确认无误后在下方列表点击「开始编译」。
      </p>
      <div className="flex flex-col gap-3 md:flex-row md:items-center">
        <input
          ref={inputRef}
          id="knowledge-upload-input"
          type="file"
          accept=".pdf,.docx,.md,.txt"
          className="sr-only"
          onChange={(event) => {
            setFile(event.target.files?.[0] ?? null);
            setError(null);
            setMessage(null);
          }}
        />
        <Button
          type="button"
          variant="outline"
          onClick={() => inputRef.current?.click()}
        >
          <FileUp className="size-4" />
          选择文件
        </Button>
        <span className="min-w-0 flex-1 truncate text-sm text-zinc-600">
          {file ? file.name : "未选择文件"}
        </span>
        <Button
          type="button"
          disabled={!file || pending}
          onClick={() => void upload()}
        >
          <Upload className="size-4" />
          {pending ? "上传中…" : "上传至队列"}
        </Button>
      </div>
      {message ? (
        <p className="mt-3 text-sm text-emerald-700">{message}</p>
      ) : null}
      {error ? <p className="mt-3 text-sm text-red-600">{error}</p> : null}
    </div>
  );
}
