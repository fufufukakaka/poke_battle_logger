import {
  Box,
  Container,
  Heading,
  Stack,
  Table,
  Tbody,
  Td,
  Th,
  Thead,
  Tr,
  Divider,
  Badge,
} from '@chakra-ui/react';
import PokeStatGroup from '../components/data-display/poke-stat-group';
import useSWR from "swr";
import axios from "axios"
import { withAuthenticationRequired } from '@auth0/auth0-react';

interface DashBoardProps {
  latest_lose_pokemon: string;
  latest_rank: number;
  latest_win_pokemon: string;
  win_rate: number;
  recent_battle_history: {
    battle_id: string;
    created_at: string;
    next_rank: number;
    opponent_pokemon_1: string;
    win_or_lose: string;
    your_pokemon_1: string;
  }[];
}

export const fetcher = async (url: string) => {
  const results = await axios.get(url);
  const data = await {
    latest_lose_pokemon: results.data.latest_lose_pokemon,
    latest_rank: results.data.latest_rank,
    latest_win_pokemon: results.data.latest_win_pokemon,
    win_rate: results.data.win_rate,
    recent_battle_history: [
      ...results.data.recent_battle_history.map(
        (battle: {
          battle_id: string;
          created_at: string;
          next_rank: number;
          opponent_pokemon_1: string;
          win_or_lose: string;
          your_pokemon_1: string;
        }) => ({
          battle_id: battle.battle_id,
          created_at: battle.created_at,
          next_rank: Number(battle.next_rank),
          opponent_pokemon_1: battle.opponent_pokemon_1,
          win_or_lose: battle.win_or_lose,
          your_pokemon_1: battle.your_pokemon_1,
        })
      ),
    ],
  }
  return data;
}

const Dashboard: React.FC<DashBoardProps> = ({
}) => {
  const { data, error, isLoading } = useSWR(
    "http://127.0.0.1:8000/api/v1/recent_battle_summary",
    fetcher
  )

  if (isLoading) return <p>loading...</p>
  if (error) return <p>error</p>
  if (!data) return <p>no data</p>

  return (
    <Box bg="gray.50" minH="100vh">
      <Container maxW="container.xl" py="8">
        <Heading padding={'5px'}>ダッシュボード</Heading>
        <Box flex="1" p="4" bg="white">
          <Stack spacing={4}>
            <PokeStatGroup
              latest_lose_pokemon={data.latest_lose_pokemon}
              latest_rank={data.latest_rank}
              latest_win_pokemon={data.latest_win_pokemon}
              win_rate={Number(data.win_rate.toFixed(4))}
            />
            <Divider />
            <Heading size="md" padding={'5px'}>
              最近の対戦履歴
            </Heading>
            <Table>
              <Thead>
                <Tr>
                  <Th>対戦ID</Th>
                  <Th>対戦日時</Th>
                  <Th>勝敗</Th>
                  <Th>順位</Th>
                  <Th>自分の初手</Th>
                  <Th>相手の初手</Th>
                </Tr>
              </Thead>
              <Tbody>
                {data.recent_battle_history.map((battle) => (
                  <Tr key={battle.battle_id}>
                    <Td>{battle.battle_id}</Td>
                    <Td>{battle.created_at}</Td>
                    <Td>
                      {battle.win_or_lose === 'win' ? (
                        <Badge colorScheme="green">勝利！</Badge>
                      ) : (
                        <Badge colorScheme="red">負け</Badge>
                      )}
                    </Td>
                    <Td>{battle.next_rank}</Td>
                    <Td>{battle.your_pokemon_1}</Td>
                    <Td>{battle.opponent_pokemon_1}</Td>
                  </Tr>
                ))}
              </Tbody>
            </Table>
          </Stack>
        </Box>
      </Container>
    </Box>
  );
};

export default withAuthenticationRequired(Dashboard);
