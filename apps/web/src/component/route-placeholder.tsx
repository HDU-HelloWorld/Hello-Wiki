// 该组件仅作为路由占位符，用于在路由构建过程中，避免出现 404 错误，路由对应均页面开发完成后再删除

export function RoutePlaceholder({ title }: { title: string }) {
  return (
    <div className="flex min-h-full flex-col bg-white p-8">
      <h1 className="text-xl font-semibold text-zinc-900">{title}</h1>
      <p className="mt-2 text-sm text-zinc-500">页面建设中</p>
    </div>
  );
}
