import {
  Card,
  Heading,
  CardBody,
  Flex,
  Text,
  Badge,
  Divider,
  CardFooter,
  Button,
  Skeleton,
  useToast,
} from '@chakra-ui/react';
import { useDisclosure } from '@chakra-ui/react'
import { TimeIcon, CopyIcon } from '@chakra-ui/icons';
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
  const { isOpen, onOpen, onClose } = useDisclosure()
  const [shouldFetch, setShouldFetch] = useState(false)
  const toast = useToast()

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
          status: 'success',
          duration: 2000,
          isClosable: true,
        })
        setShouldFetch(false)
      } catch (error) {
        toast({
          title: 'エラーが発生しました',
          description: 'クリップボードへのコピーに失敗しました',
          status: 'error',
          duration: 3000,
          isClosable: true,
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
        status: 'error',
        duration: 3000,
        isClosable: true,
      })
      setShouldFetch(false)
    }
  }, [error, shouldFetch, toast])

  return (
    <>
    <BattleLogDetailModal
      isOpen={isOpen}
      onClose={onClose}
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
      <Skeleton isLoaded={!isLoading}>
      <CardBody>
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
        <Heading size={"xs"}>MatchUp</Heading>
        <Flex>
          {
            your_pokemon_team.split(',').map((pokemon_name) => (
              <PokemonIcon key={pokemon_name} pokemon_name={pokemon_name} boxSize={'40px'} />
            ))
          }
        </Flex>
        <Text>VS</Text>
        <Flex>
          {
            opponent_pokemon_team.split(',').map((pokemon_name) => (
              <PokemonIcon key={pokemon_name} pokemon_name={pokemon_name} boxSize={'40px'} />
            ))
          }
        </Flex>
        <Divider margin={'5px'} />
        <Heading size={"xs"}>Selection</Heading>
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
        <Heading size={"xs"}>📝 Memo</Heading>
        <Text>
          {memo}
        </Text>
      </CardBody>
      <CardFooter>
        <Flex gap={2}>
          <Button onClick={onOpen} variant='solid' colorScheme='blue'>
            詳細を確認する
          </Button>
          <Button 
            onClick={copyBattleLog} 
            variant='outline' 
            colorScheme='gray'
            leftIcon={<CopyIcon />}
            isLoading={isFetchingLog}
            loadingText='取得中...'
          >
            対戦ログをコピー
          </Button>
        </Flex>
      </CardFooter>
      </Skeleton>
    </Card>
    </>
  );
};

export default BattleLogCard;
