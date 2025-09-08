import React from 'react';
import Link from 'next/link';
import { RiDatabaseFill } from 'react-icons/ri';
import { MdCatchingPokemon } from 'react-icons/md';
import { MdLogout } from 'react-icons/md';
import { TbAnalyzeFilled } from 'react-icons/tb';
import { useAuth0 } from '@auth0/auth0-react';
import { AiOutlinePlusSquare } from 'react-icons/ai';
import { BiImages } from 'react-icons/bi';
import { useRouter } from 'next/router';

import { Button } from '@/components/ui/button';
import { Avatar, AvatarImage, AvatarFallback } from '@/components/ui/avatar';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import {
  Sidebar,
  SidebarContent,
  SidebarHeader,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupLabel,
  SidebarGroupContent,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarTrigger,
} from '@/components/ui/sidebar';

interface SidebarProps {
  onClose: () => void;
  setSeason: (season: number) => void;
  seasonList?: { season: number; seasonStartEnd: string }[];
  season: number;
  className?: string;
}

const dashboardItem = {
  title: 'ダッシュボード',
  href: '/',
  icon: MdCatchingPokemon,
};

const analyticsItems = [
  {
    title: 'ログ分析',
    href: '/analytics',
    icon: TbAnalyzeFilled,
  },
  {
    title: '対戦ログ一覧',
    href: '/battle_log',
    icon: RiDatabaseFill,
  },
];

const dataManagementItems = [
  {
    title: '対戦データの登録',
    href: '/process_video',
    icon: AiOutlinePlusSquare,
  },
  {
    title: '画像のラベリング',
    href: '/annotate_pokemon_images',
    icon: BiImages,
  },
];

const SideBar = ({ onClose, setSeason, seasonList, season, className }: SidebarProps) => {
  const { user, isAuthenticated, logout } = useAuth0();
  const router = useRouter();

  return (
    <Sidebar className={className}>
      <SidebarHeader className="py-3 px-4 space-y-2">
        <div className="flex items-center justify-between">
          <Link href="/" className="text-xl font-mono font-bold text-sidebar-foreground">
            Poke Battle Logger
          </Link>
          <div className="md:hidden">
            <SidebarTrigger onClick={onClose} />
          </div>
        </div>
        
        <div>
          <Select value={season.toString()} onValueChange={(value) => setSeason(Number(value))}>
            <SelectTrigger className="text-sidebar-foreground bg-transparent border-sidebar-border h-8">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {seasonList ? seasonList.map((season) => (
                <SelectItem key={season.season} value={season.season.toString()}>
                  {season.seasonStartEnd}
                </SelectItem>
              )) : null}
            </SelectContent>
          </Select>
        </div>
      </SidebarHeader>
      
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupContent>
            <SidebarMenu>
              <SidebarMenuItem>
                <SidebarMenuButton asChild isActive={router.pathname === dashboardItem.href}>
                  <Link href={dashboardItem.href}>
                    <MdCatchingPokemon className="mr-2 h-4 w-4" />
                    <span>{dashboardItem.title}</span>
                  </Link>
                </SidebarMenuButton>
              </SidebarMenuItem>
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>

        <SidebarGroup>
          <SidebarGroupLabel>分析</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {analyticsItems.map((item) => {
                const Icon = item.icon;
                const isActive = router.pathname === item.href;
                
                return (
                  <SidebarMenuItem key={item.href}>
                    <SidebarMenuButton asChild isActive={isActive}>
                      <Link href={item.href}>
                        <Icon className="mr-2 h-4 w-4" />
                        <span>{item.title}</span>
                      </Link>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                );
              })}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>

        <SidebarGroup>
          <SidebarGroupLabel>データ管理</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {dataManagementItems.map((item) => {
                const Icon = item.icon;
                const isActive = router.pathname === item.href;
                
                return (
                  <SidebarMenuItem key={item.href}>
                    <SidebarMenuButton asChild isActive={isActive}>
                      <Link href={item.href}>
                        <Icon className="mr-2 h-4 w-4" />
                        <span>{item.title}</span>
                      </Link>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                );
              })}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
      
      <SidebarFooter className="p-4">
        {isAuthenticated && user && (
          <div className="flex flex-col items-center space-y-2">
            <Avatar className="h-12 w-12">
              <AvatarImage src={user.picture} alt={user.name} />
              <AvatarFallback>{user.name?.charAt(0)}</AvatarFallback>
            </Avatar>
            <Button
              variant="outline"
              size="sm"
              className="w-full"
              onClick={() =>
                logout({
                  logoutParams: { returnTo: 'http://localhost:3000/login' },
                })
              }
            >
              <MdLogout className="mr-2 h-4 w-4" />
              ログアウト
            </Button>
          </div>
        )}
      </SidebarFooter>
    </Sidebar>
  );
};

export default SideBar;
