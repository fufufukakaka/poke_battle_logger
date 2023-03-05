import {
  Box,
  Container,
  Stack,
  Table,
  Tbody,
  Td,
  Th,
  Thead,
  Tr,
} from '@chakra-ui/react';
import { GetServerSideProps } from 'next';
import getRecentSummaryHandler from './api/get_recent_summary';
import PokeStatGroup from './components/data-display/poke-stat-group';

interface DashBoardProps {
  latest_lose_pokemon: string;
  latest_win_pokemon_image: string;
  latest_rank: number;
  latest_win_pokemon: string;
  latest_lose_pokemon_image: string;
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

export const getServerSideProps: GetServerSideProps<
  DashBoardProps
> = async () => {
  const result = await getRecentSummaryHandler();

  if ('error' in result) {
    throw new Error('error');
  }

  return {
    props: {
      latest_lose_pokemon: result.latest_lose_pokemon,
      latest_lose_pokemon_image: result.latest_lose_pokemon_image,
      latest_rank: result.latest_rank,
      latest_win_pokemon: result.latest_win_pokemon,
      latest_win_pokemon_image: result.latest_win_pokemon_image,
      win_rate: result.win_rate,
      recent_battle_history: [
        ...result.recent_battle_history.map(
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
    },
  };
};

const Dashboard: React.FC<DashBoardProps> = ({
  latest_lose_pokemon,
  latest_lose_pokemon_image,
  latest_rank,
  latest_win_pokemon,
  latest_win_pokemon_image,
  win_rate,
  recent_battle_history
}) => {
  return (
    <Box bg="gray.50" minH="100vh">
      <Container maxW="container.xl" py="8">
        <Box flex="1" p="4" bg="white">
          <Stack spacing={4}>
            <PokeStatGroup
              latest_lose_pokemon={latest_lose_pokemon}
              latest_lose_pokemon_image={latest_lose_pokemon_image}
              latest_rank={latest_rank}
              latest_win_pokemon={latest_win_pokemon}
              latest_win_pokemon_image={latest_win_pokemon_image}
              win_rate={Number(win_rate.toFixed(4))}
            />
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
                {recent_battle_history.map((battle) => (
                  <Tr key={battle.battle_id}>
                    <Td>{battle.battle_id}</Td>
                    <Td>{battle.created_at}</Td>
                    <Td>{battle.win_or_lose}</Td>
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

export default Dashboard;
