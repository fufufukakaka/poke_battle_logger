import React from 'react';
import Link from 'next/link';
import { RiDatabaseFill } from 'react-icons/ri';
import NavItem from '../atoms/NavItem';
import { MdCatchingPokemon } from 'react-icons/md';
import { MdLogout } from 'react-icons/md';
import { TbAnalyzeFilled } from 'react-icons/tb';
import { useAuth0 } from '@auth0/auth0-react';
import { AiOutlinePlusSquare } from 'react-icons/ai';
import { BiImages } from 'react-icons/bi';
import { X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarImage, AvatarFallback } from '@/components/ui/avatar';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { cn } from '@/lib/utils';

interface SidebarProps {
  onClose: () => void;
  setSeason: (season: number) => void;
  seasonList?: { season: number; seasonStartEnd: string }[];
  season: number;
  className?: string;
}

const SideBar = ({ onClose, setSeason, seasonList, season, className }: SidebarProps) => {
  const { user, isAuthenticated, logout } = useAuth0();
  return (
    <div
      className={cn(
        "bg-[rgba(11,21,48,0.9)] dark:bg-gray-900 border-r border-gray-200 dark:border-gray-700 w-full md:w-60 fixed h-full",
        className
      )}
    >
      <div className="h-20 flex items-center mx-8 justify-between my-5">
        <span className="text-2xl font-mono font-bold text-white">
          <Link href="/">Poke Battle Logger</Link>
        </span>
        <Button
          variant="ghost"
          size="icon"
          className="md:hidden text-white hover:text-gray-300"
          onClick={onClose}
        >
          <X className="h-4 w-4" />
        </Button>
      </div>
      <div className="px-4 mb-4">
        <Select value={season.toString()} onValueChange={(value) => setSeason(Number(value))}>
          <SelectTrigger className="text-white bg-transparent border-gray-600">
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
      <NavItem
        key={'dashboard'}
        icon={MdCatchingPokemon}
        href={'/'}
        className="mb-1"
      >
        ダッシュボード
      </NavItem>
      <NavItem
        key={'analytics'}
        icon={TbAnalyzeFilled}
        href={'/analytics'}
        className="mt-1"
      >
        ログ分析
      </NavItem>
      <NavItem
        key={'battle_log'}
        icon={RiDatabaseFill}
        href={'/battle_log'}
        className="mt-1"
      >
        対戦ログ一覧
      </NavItem>
      <NavItem
        key={'process_video'}
        icon={AiOutlinePlusSquare}
        href={'/process_video'}
        className="mt-1"
      >
        対戦データの登録
      </NavItem>
      <NavItem
        key={'annotate_pokemon_images'}
        icon={BiImages}
        href={'/annotate_pokemon_images'}
        className="mt-1"
      >
        画像のラベリング
      </NavItem>
      <div className="flex items-center p-4 mx-4 rounded-lg cursor-pointer text-white break-all">
        {isAuthenticated && user ? (
          <div className="flex flex-col items-center w-full">
            <Avatar className="h-14 w-14 mb-3">
              <AvatarImage src={user.picture} alt={user.name} />
              <AvatarFallback>{user.name?.charAt(0)}</AvatarFallback>
            </Avatar>
            <Button
              className="mt-2"
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
        ) : null}
      </div>
    </div>
  );
};

export default SideBar;
