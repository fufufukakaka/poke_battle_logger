import { Chrono } from "react-chrono";
import PokemonIcon from "../atoms/pokemon-icon";
import { Box, Flex } from "@chakra-ui/react";
import {
  Badge,
  ListItem,
  OrderedList,
  Switch,
  FormControl,
  FormLabel,
} from '@chakra-ui/react'
import { useState } from "react";

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

  return (
    <>
      <FormControl display='flex' alignItems='center'>
        <FormLabel htmlFor='show-message' mb='0'>
          <Badge colorScheme='purple'>BETA</Badge> Show Battle Log Message
        </FormLabel>
        <Switch id='show-message' onChange={(e) => setShowMessage(!showMessage)} />
      </FormControl>
      <Chrono
        mode="VERTICAL"
        cardHeight={100}
        allowDynamicUpdate={true}
      >
        {in_battle_log.map((log) => (
          <Box key={log.turn}>
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
            <OrderedList>
              {
                (message_log.filter((message) => Number(message.turn) === Number(log.turn)).map((message) => (
                  <ListItem key={message.frame_number}>{message.message}</ListItem>
                )))
              }
            </OrderedList>
          </Box>
        ))}
      </Chrono>
    </>
  );
};

export default InBattleTimeline;
