import {
  Heading,
  Flex,
  Text,
  Badge,
  Divider,
  Editable,
  EditableTextarea,
  EditablePreview,
  VStack,
  HStack,
} from '@chakra-ui/react';
import {
  Modal,
  ModalOverlay,
  ModalContent,
  ModalHeader,
  ModalBody,
  ModalCloseButton,
} from '@chakra-ui/react';
import { TimeIcon } from '@chakra-ui/icons';
import PokemonIcon from '../atoms/pokemon-icon';
import ReactPlayer from 'react-player/youtube'
import { Tabs, TabList, TabPanels, Tab, TabPanel, TabIndicator } from '@chakra-ui/react'
import {
  Accordion,
  AccordionItem,
  AccordionButton,
  AccordionPanel,
  AccordionIcon,
  Box,
} from '@chakra-ui/react'
import InBattleTimeline from '../data-display/in-battle-timeline'
import useSWR from 'swr';
import axios from 'axios';
import { useState } from 'react';

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
    <Modal isOpen={isOpen} onClose={onClose} size={"xl"}>
      <ModalOverlay />
      <ModalContent>
        <ModalHeader>対戦詳細</ModalHeader>
        <ModalCloseButton />
        <ModalBody>
          <Accordion allowToggle>
            <AccordionItem>
              <h2>
                <AccordionButton>
                  <Box as="span" flex='1' textAlign='left'>
                    Movie
                  </Box>
                  <AccordionIcon />
                </AccordionButton>
              </h2>
              <AccordionPanel pb={4}>
                <ReactPlayer url={video} controls={true} width={"100%"}/>
              </AccordionPanel>
            </AccordionItem>
          </Accordion>
          <Text>
            <TimeIcon boxSize={4} margin={'5px'} />
            {battle_created_at}
          </Text>
          <Text>
            {win_or_lose === 'win' ? (
              <Badge colorScheme="green">勝利！</Badge>
            ) : (
              <Badge colorScheme="red">負け</Badge>
            )}{' '}
            → 👑 {next_rank}
          </Text>
          <Divider margin={'5px'} />
          <Tabs position="relative" variant="unstyled">
            <TabList>
              <Tab>Selection</Tab>
              <Tab>In-Battle</Tab>
            </TabList>
            <TabIndicator
              mt="-1.5px"
              height="2px"
              bg="blue.500"
              borderRadius="1px"
            />
            <TabPanels>
              <TabPanel>
              <Heading size={'xs'}>ShowDown</Heading>
                <Flex>
                  {your_pokemon_team.split(',').map((pokemon_name) => (
                    <PokemonIcon
                      key={pokemon_name}
                      pokemon_name={pokemon_name}
                      boxSize={'40px'}
                    />
                  ))}
                </Flex>
                <Text>VS</Text>
                <Flex>
                  {opponent_pokemon_team.split(',').map((pokemon_name) => (
                    <PokemonIcon
                      key={pokemon_name}
                      pokemon_name={pokemon_name}
                      boxSize={'40px'}
                    />
                  ))}
                </Flex>
                <Divider margin={'5px'} />
                <Heading size={'xs'}>Selection</Heading>
                <Flex>
                  <PokemonIcon pokemon_name={your_pokemon_select1} boxSize={'50px'} />
                  <PokemonIcon pokemon_name={your_pokemon_select2} boxSize={'50px'} />
                  <PokemonIcon pokemon_name={your_pokemon_select3} boxSize={'50px'} />
                </Flex>
                <Text>VS</Text>
                <Flex>
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
                </Flex>
                <Divider margin={'5px'} />
                <Heading size={'xs'}>Fainted Log</Heading>
                <VStack alignItems={'baseline'}>
                  {faintedLogDataIsLoading ? (
                    <Text>loading...</Text>
                  // if not error
                  ) : faintedLogDataError ? null : faintedLogData ? (
                    faintedLogData.map((log) => (
                      <Box key={log.turn}>
                        <HStack>
                          <PokemonIcon
                            key={log.turn}
                            pokemon_name={log.your_pokemon_name}
                            boxSize={'50px'}
                          />
                          {log.fainted_pokemon_side === 'Your Pokemon Win' ? <Text>🏆:🥲</Text> : <Text>🥲:🏆</Text>}
                          <PokemonIcon
                            key={log.turn}
                            pokemon_name={log.opponent_pokemon_name}
                            boxSize={'50px'}
                          />
                        </HStack>
                        <Text>Turn: {log.turn}</Text>
                      </Box>
                    ))
                  ) : null}
                </VStack>
                <Divider margin={'5px'} />
                <Heading size={'xs'}>📝 Memo</Heading>
                <Editable defaultValue={memo} onChange={value => (setInputText(value))} value={inputText} onSubmit={value => saveMemo(battle_id, value)}>
                  <EditablePreview />
                  <EditableTextarea />
                </Editable>
              </TabPanel>
              <TabPanel>
                {!error && !isLoading && data && messageData ? <InBattleTimeline in_battle_log={data} message_log={messageData}/> : null}
              </TabPanel>
            </TabPanels>
          </Tabs>
        </ModalBody>
      </ModalContent>
    </Modal>
  );
};

export default BattleLogDetailModal;
