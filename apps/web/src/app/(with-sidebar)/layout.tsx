import SideBar from "@/component/side-bar";

export default function WithSidebarLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <div className="flex min-h-dvh w-full bg-white">
      <SideBar />
      <main className="min-h-dvh min-w-0 flex-1 overflow-auto bg-white">{children}</main>
    </div>
  );
}
