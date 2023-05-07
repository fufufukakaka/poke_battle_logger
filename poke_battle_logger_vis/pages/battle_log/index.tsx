import {
  HStack,
  Image,
  Box,
  Container,
  SimpleGrid,
  Heading,
} from '@chakra-ui/react';
import useSWR from 'swr';
import { useContext, useEffect, useState } from 'react';
import { SeasonContext } from '../_app';
import BattleLogCard from '@/components/data-display/battle-log-card';
import { useAuth0, withAuthenticationRequired } from '@auth0/auth0-react';
import PaginationController from '@/components/navigation/pagination-controller';
import axiosInstance from '../../helper/axios'

interface BattleLogProps {
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
  memo: string
  video: string
}

const fetcher = async (url: string) => {
  const results = await axiosInstance.get(url);
  // results.data は BattleLogProps の配列
  return await results.data;
};

const BattleLogs: React.FC = () => {
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(6);

  const { user } = useAuth0();
  const season = useContext(SeasonContext);

  const { data: battleCountData, error: battleCountError } = useSWR(
    `/api/v1/battle_log_count?trainer_id=${user?.sub?.replace("|", "_")}&season=${season}`,
    fetcher
  );

  const { data, error, mutate, isLoading } = useSWR(
    `/api/v1/battle_log?trainer_id=${user?.sub?.replace("|", "_")}&season=${season}&page=${currentPage}&size=${pageSize}`,
    fetcher
  );

  const saveMemo = async (battle_id: string, memo: string) => {
    await axiosInstance.post(
      `api/v1/update_memo`,
      {
        battle_id: battle_id,
        memo: memo,
      }
    )
    mutate(data.map((battle: BattleLogProps) => {
      if (battle.battle_id === battle_id) {
        return {...battle, memo: memo}
      }
      return battle
    })
    )
  };

  if (error || battleCountError) return <p>error</p>;
  if (!isLoading && (!data || !battleCountData)) return <p>no data</p>;

  let maxPage = battleCountData ? Math.ceil(battleCountData / pageSize) : 10;

  return (
    <Box bg="gray.50" minH="100vh">
      <Container maxW="container.xl" py="8">
        <HStack spacing={0}>
          <Heading padding={'5px'}>対戦一覧</Heading>
          <Image src="./n426.gif" alt="フワライド" boxSize="50px" />
          <PaginationController
            maxPage={maxPage}
            currentPage={currentPage}
            setCurrentPage={setCurrentPage}
          />
        </HStack>
        <Box flex="1" p="4" bg="white">
          <SimpleGrid columns={3} spacing={10}>
            {data ? data.map((battle: BattleLogProps) => (
              <BattleLogCard
                key={battle.battle_id}
                battle_id={battle.battle_id}
                battle_created_at={battle.battle_created_at}
                win_or_lose={battle.win_or_lose}
                next_rank={battle.next_rank}
                your_pokemon_team={battle.your_pokemon_team}
                opponent_pokemon_team={battle.opponent_pokemon_team}
                your_pokemon_select1={battle.your_pokemon_select1}
                your_pokemon_select2={battle.your_pokemon_select2}
                your_pokemon_select3={battle.your_pokemon_select3}
                opponent_pokemon_select1={battle.opponent_pokemon_select1}
                opponent_pokemon_select2={battle.opponent_pokemon_select2}
                opponent_pokemon_select3={battle.opponent_pokemon_select3}
                memo={battle.memo}
                video={battle.video}
                saveMemo={saveMemo}
                isLoading={isLoading}
              />
            )) : null }
          </SimpleGrid>
        </Box>
      </Container>
    </Box>
  );
};

export default withAuthenticationRequired(BattleLogs);
