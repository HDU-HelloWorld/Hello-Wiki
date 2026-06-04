import Link from "next/link";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

export default function LoginPage() {
  return (
    <main className="flex min-h-dvh bg-[#F6F7FB]">
      <section className="hidden flex-1 bg-gradient-to-br from-blue-600 to-indigo-700 p-10 text-white lg:flex lg:flex-col lg:justify-between">
        <div className="flex items-center gap-3">
          <div className="flex size-12 items-center justify-center rounded-2xl bg-white/15 text-xl font-semibold">
            知
          </div>
          <div>
            <div className="text-xl font-semibold">知原</div>
            <div className="text-sm text-blue-100">编译式 Wiki 智能客服</div>
          </div>
        </div>
        <div>
          <h1 className="max-w-xl text-4xl font-semibold leading-tight">
            让知识真正被理解，而非被检索。
          </h1>
          <p className="mt-4 max-w-xl text-sm leading-7 text-blue-100">
            文档上传、AI 编译、Wiki
            构建、智能问答、未知沉淀和持续优化，在同一个系统里闭环。
          </p>
        </div>
      </section>
      <section className="flex flex-1 items-center justify-center px-6 py-10">
        <div className="w-full max-w-md rounded-3xl border border-zinc-200 bg-white p-8 shadow-sm">
          <h2 className="text-2xl font-semibold text-zinc-950">登录知原</h2>
          <p className="mt-2 text-sm text-zinc-500">
            当前为前端原型页面，鉴权能力待后续接入。
          </p>
          <div className="mt-6 space-y-4">
            <label className="space-y-2">
              <span className="text-sm font-medium text-zinc-700">邮箱</span>
              <Input placeholder="admin@example.com" />
            </label>
            <label className="space-y-2">
              <span className="text-sm font-medium text-zinc-700">密码</span>
              <Input placeholder="请输入密码" type="password" />
            </label>
            <Button asChild className="w-full">
              <Link href="/home">进入工作台</Link>
            </Button>
          </div>
        </div>
      </section>
    </main>
  );
}
