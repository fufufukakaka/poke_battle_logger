import { Chrono } from "react-chrono";
import PokemonIcon from "../atoms/pokemon-icon";
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Loader2 } from 'lucide-react';
import { useEffect, useState } from "react";

interface InBattleTimelineProps {
  in_battle_log: {
    turn: number;
    frame_number: number;
    your_pokemon_name: string;
    opponent_pokemon_name: string;
  }[]
  message_log: {
    turn: number;
    frame_number: number;
    message: string;
  }[]
}

const InBattleTimeline: React.FC<InBattleTimelineProps> = ({ in_battle_log, message_log }) => {
  const [showMessage, setShowMessage] = useState(false);
  const [renderKey, setRenderKey] = useState(Date.now());
  const [loading, setLoading] = useState(false); // New state for loading

  const toggleShowMessage = () => {
    setShowMessage(!showMessage);
    setLoading(true); // Set loading to true before re-rendering
    setRenderKey(Date.now());
  };

  useEffect(() => {
    if (loading) {
      setLoading(false); // Set loading to false after re-rendering
    }
  }, [loading, renderKey]); // React on renderKey change

  return (
    <>
      <div className="flex items-center space-x-4 mb-4">
        <Label htmlFor='show-message' className="flex items-center space-x-2 text-sm font-medium">
          <Badge variant="secondary" className="bg-purple-100 text-purple-800">BETA</Badge>
          <span>Show Battle Log Message</span>
        </Label>
        <Switch id='show-message' onCheckedChange={toggleShowMessage} />
      </div>
      {loading ? (
        <div className="flex items-center justify-center p-4">
          <Loader2 className="h-6 w-6 animate-spin" />
        </div>
      ) : (
      <Chrono
        key={renderKey}
        mode="VERTICAL"
        cardHeight={100}
        allowDynamicUpdate={true}
      >
        {in_battle_log.map((log) => (
          <div key={log.turn} className="space-y-2">
            <h3 className="text-lg font-semibold">Turn: {log.turn}</h3>
            <div className="flex items-end space-x-2">
              <PokemonIcon
                pokemon_name={log.your_pokemon_name}
                boxSize={'50px'}
              />
              <p className="text-sm font-medium">VS</p>
              <PokemonIcon
                pokemon_name={log.opponent_pokemon_name}
                boxSize={'50px'}
              />
            </div>
            {showMessage ? (
              <ol className="list-decimal list-inside space-y-1 text-sm">
                {message_log.filter((message) => Number(message.turn) === Number(log.turn)).map((message) => (
                  <li key={message.frame_number}>{message.message}</li>
                ))}
              </ol>
            ) : null}
          </div>
        ))}
      </Chrono>
      )}
    </>
  );
};

export default InBattleTimeline;
