import { Card, CardContent, CardFooter } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import { Skeleton } from '@/components/ui/skeleton';
import { useToast } from '@/hooks/use-toast';
import { Clock, Copy } from 'lucide-react';
import PokemonIcon from '../atoms/pokemon-icon';
import BattleLogDetailModal from './battle-log-detail-model';
import { useState, useEffect } from 'react';
import useSWR from 'swr';

interface BattleLogCardProps {
  battle_id: string;
  battle_created_at: string;
  win_or_lose: string;
  next_rank: number;
  your_pokemon_team: string;
  opponent_pokemon_team: string;
  your_pokemon_select1: string;
  your_pokemon_select2: string;
  your_pokemon_select3: string;
  opponent_pokemon_select1: string;
  opponent_pokemon_select2: string;
  opponent_pokemon_select3: string;
  memo: string;
  video: string;
  saveMemo: (battle_id: string, memo: string) => void;
  isLoading: boolean;
}

const BattleLogCard: React.FunctionComponent<BattleLogCardProps> = ({
  battle_id,
  battle_created_at,
  win_or_lose,
  next_rank,
  your_pokemon_team,
  opponent_pokemon_team,
  your_pokemon_select1,
  your_pokemon_select2,
  your_pokemon_select3,
  opponent_pokemon_select1,
  opponent_pokemon_select2,
  opponent_pokemon_select3,
  memo,
  video,
  saveMemo,
  isLoading
}) => {
  const [isOpen, setIsOpen] = useState(false)
  const [shouldFetch, setShouldFetch] = useState(false)
  const { toast } = useToast()

  const fetcher = (url: string) => fetch(url).then(res => res.json())
  
  const { data, error, isLoading: isFetchingLog } = useSWR(
    shouldFetch ? `/api/get_in_battle_message_full_log?battle_id=${battle_id}` : null,
    fetcher
  )

  const copyBattleLog = async () => {
    if (!shouldFetch) {
      setShouldFetch(true)
      return
    }
    
    if (data) {
      try {
        // Format the battle log data into a readable string
        const logText = JSON.stringify(data, null, 2)
        
        await navigator.clipboard.writeText(logText)
        toast({
          title: '対戦ログをコピーしました',
        })
        setShouldFetch(false)
      } catch (error) {
        toast({
          title: 'エラーが発生しました',
          description: 'クリップボードへのコピーに失敗しました',
          variant: 'destructive',
        })
      }
    }
  }

  // Handle data fetching and copying
  useEffect(() => {
    if (data && shouldFetch) {
      copyBattleLog()
    }
  }, [data, shouldFetch])

  // Handle error
  useEffect(() => {
    if (error && shouldFetch) {
      toast({
        title: 'エラーが発生しました',
        description: '対戦ログの取得に失敗しました',
        variant: 'destructive',
      })
      setShouldFetch(false)
    }
  }, [error, shouldFetch, toast])

  return (
    <>
    <BattleLogDetailModal
      isOpen={isOpen}
      onClose={() => setIsOpen(false)}
      battle_id={battle_id}
      battle_created_at={battle_created_at}
      win_or_lose={win_or_lose}
      next_rank={next_rank}
      your_pokemon_team={your_pokemon_team}
      opponent_pokemon_team={opponent_pokemon_team}
      your_pokemon_select1={your_pokemon_select1}
      your_pokemon_select2={your_pokemon_select2}
      your_pokemon_select3={your_pokemon_select3}
      opponent_pokemon_select1={opponent_pokemon_select1}
      opponent_pokemon_select2={opponent_pokemon_select2}
      opponent_pokemon_select3={opponent_pokemon_select3}
      memo={memo}
      video={video}
      saveMemo={saveMemo}
    />
    <Card>
      {isLoading ? (
        <Skeleton className="h-[400px] w-full" />
      ) : (
        <>
          <CardContent className="pt-6">
            <div className="flex items-center gap-2 mb-2">
              <Clock className="h-4 w-4" />
              <span className="text-sm">{battle_created_at}</span>
            </div>
            <div className="flex items-center gap-2 mb-4">
              {win_or_lose === 'win' ? (
                <Badge className="bg-green-100 text-green-800 hover:bg-green-100">勝利！</Badge>
              ) : (
                <Badge className="bg-red-100 text-red-800 hover:bg-red-100">負け</Badge>
              )}
              <span>→ 👑 {next_rank}</span>
            </div>
            <Separator className="my-3" />
            <h3 className="text-sm font-semibold mb-2">MatchUp</h3>
            <div className="flex justify-center gap-1 mb-2">
              {
                your_pokemon_team.split(',').map((pokemon_name) => (
                  <PokemonIcon key={pokemon_name} pokemon_name={pokemon_name} boxSize={'51px'} />
                ))
              }
            </div>
            <p className="text-xs text-center text-gray-500">VS</p>
            <div className="flex justify-center gap-1 mb-3">
              {
                opponent_pokemon_team.split(',').map((pokemon_name) => (
                  <PokemonIcon key={pokemon_name} pokemon_name={pokemon_name} boxSize={'51px'} />
                ))
              }
            </div>
            <Separator className="my-3" />
            <h3 className="text-sm font-semibold mb-2">Selection</h3>
            <div className="flex justify-center gap-2 mb-2">
              <PokemonIcon pokemon_name={your_pokemon_select1} boxSize={'50px'} />
              <PokemonIcon pokemon_name={your_pokemon_select2} boxSize={'50px'} />
              <PokemonIcon pokemon_name={your_pokemon_select3} boxSize={'50px'} />
            </div>
            <p className="text-xs text-center text-gray-500">VS</p>
            <div className="flex justify-center gap-2 mb-3">
              <PokemonIcon
                pokemon_name={opponent_pokemon_select1}
                boxSize={'50px'}
              />
              <PokemonIcon
                pokemon_name={opponent_pokemon_select2}
                boxSize={'50px'}
              />
              <PokemonIcon
                pokemon_name={opponent_pokemon_select3}
                boxSize={'50px'}
              />
            </div>
            <Separator className="my-2" />
            <h3 className="text-sm font-semibold mb-2">📝 Memo</h3>
            <p className="text-sm text-gray-600">
              {memo || '（メモなし）'}
            </p>
          </CardContent>
          <CardFooter className="flex gap-2">
            <Button onClick={() => setIsOpen(true)}>
              詳細を確認する
            </Button>
            <Button 
              onClick={copyBattleLog} 
              variant="outline"
              disabled={isFetchingLog}
            >
              {isFetchingLog ? (
                <>取得中...</>
              ) : (
                <>
                  <Copy className="mr-2 h-4 w-4" />
                  対戦ログをコピー
                </>
              )}
            </Button>
          </CardFooter>
        </>
      )}
    </Card>
    </>
  );
};

export default BattleLogCard;
