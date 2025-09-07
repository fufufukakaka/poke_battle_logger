import React, { ReactNode } from 'react';
import SideBar from './sidebar';
import { SidebarProvider, SidebarInset, SidebarTrigger } from '@/components/ui/sidebar';

interface seasonType {
  season: number;
  seasonStartEnd: string;
}

export default function Layout({
  seasonList,
  season,
  setSeason,
  hideSidebar,
  children,
}: {
  seasonList?: seasonType[];
  season: number;
  setSeason: (season: number) => void;
  hideSidebar: boolean;
  children: ReactNode;
}) {
  if (hideSidebar) {
    return (
      <div className="min-h-screen bg-background p-4">
        {children}
      </div>
    );
  }

  return (
    <SidebarProvider>
      <SideBar
        onClose={() => {}}
        seasonList={seasonList}
        setSeason={setSeason}
        season={season}
      />
      <SidebarInset>
        <header className="sticky top-0 flex h-16 shrink-0 items-center gap-2 border-b bg-background px-4">
          <SidebarTrigger className="md:hidden" />
        </header>
        <div className="p-4">
          {children}
        </div>
      </SidebarInset>
    </SidebarProvider>
  );
}
