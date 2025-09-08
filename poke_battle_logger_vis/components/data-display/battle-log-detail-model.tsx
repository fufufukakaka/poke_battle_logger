import PokemonIcon from '../atoms/pokemon-icon';
import ReactPlayer from 'react-player/youtube'
import InBattleTimeline from '../data-display/in-battle-timeline'
import useSWR from 'swr';
import axios from 'axios';
import { useState } from 'react';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';
import { Textarea } from '@/components/ui/textarea';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion';
import { Clock, Loader } from 'lucide-react';

interface BattleLogDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
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
}

interface FaintedLogProps {
  battle_id: string;
  turn: number;
  your_pokemon_name: string;
  opponent_pokemon_name: string;
  fainted_pokemon_side: string;
}

const fetcher = async (url: string) => {
  const results = await axios.get(url);
  return await results.data;
};

const BattleLogDetailModal: React.FunctionComponent<
  BattleLogDetailModalProps
> = ({
  isOpen,
  onClose,
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
}) => {

  const { data, error, isLoading } = useSWR(
    isOpen ? `http://127.0.0.1:8000/api/v1/in_battle_log?battle_id=${battle_id}` : null,
    fetcher
  )
  const { data: messageData, error: messageDataError, isLoading: messageDataIsLoading } = useSWR(
    isOpen ? `/api/get_in_battle_message_log?battle_id=${battle_id}` : null,
    fetcher
  )
  const { data: faintedLogData, error: faintedLogDataError, isLoading: faintedLogDataIsLoading } = useSWR<FaintedLogProps[]>(
    isOpen ? `/api/get_in_battle_fainted_log?battle_id=${battle_id}` : null,
    fetcher
  )

  const [inputText, setInputText] = useState<string>(memo ? memo : 'input memo here')

  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>対戦詳細</DialogTitle>
        </DialogHeader>
        <div className="space-y-4">
          <Accordion type="single" collapsible>
            <AccordionItem value="movie">
              <AccordionTrigger>Movie</AccordionTrigger>
              <AccordionContent>
                <ReactPlayer url={video} controls={true} width={"100%"}/>
              </AccordionContent>
            </AccordionItem>
          </Accordion>
          <p className="flex items-center space-x-2">
            <Clock className="h-4 w-4" />
            <span>{battle_created_at}</span>
          </p>
          <p className="flex items-center space-x-2">
            {win_or_lose === 'win' ? (
              <Badge variant="default" className="bg-green-100 text-green-800 hover:bg-green-100">勝利！</Badge>
            ) : (
              <Badge variant="destructive">負け</Badge>
            )}
            <span>→ 👑 {next_rank}</span>
          </p>
          <Separator />
          <Tabs defaultValue="selection" className="w-full">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="selection">Selection</TabsTrigger>
              <TabsTrigger value="in-battle">In-Battle</TabsTrigger>
            </TabsList>
            <TabsContent value="selection" className="space-y-4">
              <h3 className="text-xs font-semibold mb-2">ShowDown</h3>
                <div className="flex space-x-1 mb-2">
                  {your_pokemon_team.split(',').map((pokemon_name) => (
                    <PokemonIcon
                      key={pokemon_name}
                      pokemon_name={pokemon_name}
                      boxSize={'50px'}
                    />
                  ))}
                </div>
                <p className="text-center font-medium mb-2">VS</p>
                <div className="flex space-x-1 mb-4">
                  {opponent_pokemon_team.split(',').map((pokemon_name) => (
                    <PokemonIcon
                      key={pokemon_name}
                      pokemon_name={pokemon_name}
                      boxSize={'50px'}
                    />
                  ))}
                </div>
                <Separator className="mb-4" />
                <h3 className="text-xs font-semibold mb-2">Selection</h3>
                <div className="flex space-x-1 mb-2">
                  <PokemonIcon pokemon_name={your_pokemon_select1} boxSize={'50px'} />
                  <PokemonIcon pokemon_name={your_pokemon_select2} boxSize={'50px'} />
                  <PokemonIcon pokemon_name={your_pokemon_select3} boxSize={'50px'} />
                </div>
                <p className="text-center font-medium mb-2">VS</p>
                <div className="flex space-x-1 mb-4">
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
                <Separator className="mb-4" />
                <h3 className="text-xs font-semibold mb-2">Fainted Log</h3>
                <div className="space-y-2">
                  {faintedLogDataIsLoading ? (
                    <div className="flex items-center justify-center py-4">
                      <Loader className="animate-spin h-4 w-4" />
                    </div>
                  ) : faintedLogDataError ? null : faintedLogData ? (
                    faintedLogData.map((log) => (
                      <div key={log.turn} className="space-y-1">
                        <div className="flex items-center space-x-2">
                          <PokemonIcon
                            key={log.turn}
                            pokemon_name={log.your_pokemon_name}
                            boxSize={'50px'}
                          />
                          <span className="text-sm">
                            {log.fainted_pokemon_side === 'Your Pokemon Win' ? '🏆:🥲' : '🥲:🏆'}
                          </span>
                          <PokemonIcon
                            key={log.turn}
                            pokemon_name={log.opponent_pokemon_name}
                            boxSize={'50px'}
                          />
                        </div>
                        <p className="text-sm">Turn: {log.turn}</p>
                      </div>
                    ))
                  ) : null}
                </div>
                <Separator className="mb-4" />
                <h3 className="text-xs font-semibold mb-2">📝 Memo</h3>
                <Textarea 
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                  onBlur={() => saveMemo(battle_id, inputText)}
                  placeholder="input memo here"
                  className="min-h-[80px]"
                />
            </TabsContent>
            <TabsContent value="in-battle">
              {!error && !isLoading && data && messageData ? (
                <InBattleTimeline in_battle_log={data} message_log={messageData}/>
              ) : null}
            </TabsContent>
          </Tabs>
        </div>
      </DialogContent>
    </Dialog>
  );
};

export default BattleLogDetailModal;
