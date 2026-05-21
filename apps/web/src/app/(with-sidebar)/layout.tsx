import SideBar from "@/components/side-bar";
import {
  SidebarInset,
  SidebarProvider,
  SidebarTrigger,
} from "@/components/ui/sidebar";

export default function WithSidebarLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <SidebarProvider>
      <SideBar />
      <SidebarInset className="min-h-dvh bg-background">
        <header className="flex h-12 shrink-0 items-center gap-2 border-b px-3 md:hidden">
          <SidebarTrigger />
        </header>
        <div className="min-h-0 flex-1 overflow-auto">{children}</div>
      </SidebarInset>
    </SidebarProvider>
  );
}
