import React, { ReactNode, useState } from 'react';
import SideBar from './sidebar';
import MobileNav from '../atoms/MobileNav';
import { Sheet, SheetContent, SheetTrigger } from '@/components/ui/sheet';

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
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900">
      {hideSidebar ? (
        <div className="p-4">
          {children}
        </div>
      ) : (
        <>
          <SideBar
            onClose={() => setIsOpen(false)}
            className="hidden md:block"
            seasonList={seasonList}
            setSeason={setSeason}
            season={season}
          />
          <Sheet open={isOpen} onOpenChange={setIsOpen}>
            <SheetContent side="left" className="w-full p-0">
              <SideBar 
                seasonList={seasonList} 
                season={season} 
                onClose={() => setIsOpen(false)} 
                setSeason={setSeason} 
              />
            </SheetContent>
          </Sheet>
          <MobileNav 
            className="md:hidden flex" 
            onOpen={() => setIsOpen(true)} 
          />
          <div className="ml-0 md:ml-60 p-4">
            {children}
          </div>
        </>
      )}
    </div>
  );
}
