import { Chrono } from "react-chrono";
import PokemonIcon from "../atoms/pokemon-icon";
import { Flex } from "@chakra-ui/react";

interface InBattleTimelineProps {
  in_battle_log: {
    turn: number;
    frame_number: number;
    your_pokemon_name: string;
    opponent_pokemon_name: string;
  }[]
}

const InBattleTimeline: React.FC<InBattleTimelineProps> = ({ in_battle_log }) => {
  return (
    <Chrono
      mode="VERTICAL"
    >
      {in_battle_log.map((log) => (
        <div key={log.turn}>
          <h3>Turn: {log.turn}</h3>
          <Flex alignItems={"flex-end"}>
            <PokemonIcon
              pokemon_name={log.your_pokemon_name}
              boxSize={'50px'}
            />
            <p>VS</p>
            <PokemonIcon
              pokemon_name={log.opponent_pokemon_name}
              boxSize={'50px'}
            />
          </Flex>
        </div>
      ))}
    </Chrono>
  );
};

export default InBattleTimeline;
