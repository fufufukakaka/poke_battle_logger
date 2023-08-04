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
import { withAuthenticationRequired, useAuth0 } from '@auth0/auth0-react';
import { useEffect } from "react";
import CalendarHeatmap from "react-calendar-heatmap";
import "react-calendar-heatmap/dist/styles.css";
import { ServerHost } from '../util'

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
  battle_counts: {
    battle_date: string;
    battle_count: number;
  }
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
    battle_counts: [
      ...results.data.battle_counts.map(
        (battle: {
          battle_date: string;
          battle_count: number;
        }) => ({
          date: battle.battle_date,
          count: Number(battle.battle_count),
        })
      ),
    ]
  }
  return data;
}

const Dashboard: React.FC<DashBoardProps> = ({
}) => {
  // ここで useEffect して新しいユーザだった場合、User テーブルに書き込む
  // まだ対戦履歴がないユーザだった場合は、「記録してみよう」的な文言を出す

  const oneYearAgo = new Date();
  oneYearAgo.setFullYear(oneYearAgo.getFullYear() - 1);

  const { isAuthenticated, user } = useAuth0();
  const { data, error, isLoading } = useSWR(
    `${ServerHost}/api/v1/recent_battle_summary?trainer_id=${user?.sub?.replace("|", "_")}`,
    fetcher
  )

  useEffect(() => {
    if (isAuthenticated && user && user.sub) {
      axios.post(`${ServerHost}/api/v1/save_new_trainer`, {
        trainer_id: user.sub.replace("|", "_"),
    })
  }}, [isAuthenticated, user])


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
            <Heading size="md" padding={'5px'}>活動履歴</Heading>
            <Box>
            <CalendarHeatmap
              startDate={oneYearAgo}
              endDate={new Date()}
              values={data.battle_counts}
              showWeekdayLabels={true}
              showMonthLabels={true}
              classForValue={(value) => {
                if (!value) {
                  return 'color-empty';
                } else if (value.count < 2) {
                  return `color-github-1`;
                } else if (value.count < 4) {
                  return `color-github-2`;
                } else if (value.count < 6) {
                  return `color-github-3`;
                } else {
                  return `color-github-4`;
                }
              }}
            />
            </Box>
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
