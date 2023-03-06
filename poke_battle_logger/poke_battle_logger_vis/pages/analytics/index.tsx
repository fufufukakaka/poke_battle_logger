import { HStack, Image, Box, Container, Divider, SimpleGrid, Tbody, Td, Thead, Th, Tr, Table, Heading, Spacer } from '@chakra-ui/react';
import { GetServerSideProps } from 'next';
import getWinRateTransitionHandler from '../api/get_win_rate_transition';
import getNextRankTransitionHandler from '../api/get_next_rank_transition';
import getYourPokemonSummaryHandler from '../api/get_your_pokemon_stats_summary';
import TransitionChart from '../../components/data-display/transition-chart';

interface AnalyticsProps {
  win_rates: number[];
  next_ranks: number[];
  your_pokemon_summary_result: {
    head_battle_count: number;
    head_battle_rate: number;
    in_battle_count: number;
    in_battle_rate: number;
    in_battle_win_count: number;
    in_battle_win_rate: number;
    in_team_count: number;
    in_team_rate: number;
    pokemon_name: string;
  }[];
}

export const getServerSideProps: GetServerSideProps<
  AnalyticsProps
> = async () => {
  const win_rate_result = await getWinRateTransitionHandler();
  if ('error' in win_rate_result) {
    throw new Error('error');
  }
  const next_rank_result = await getNextRankTransitionHandler();
  if ('error' in win_rate_result) {
    throw new Error('error');
  }
  const your_pokemon_summary_result = await getYourPokemonSummaryHandler();
  if ('error' in your_pokemon_summary_result) {
    throw new Error('error');
  }

  return {
    props: {
      win_rates: win_rate_result.data,
      next_ranks: next_rank_result.data,
      // convert to number
      your_pokemon_summary_result: your_pokemon_summary_result.data.map((summary: {
        head_battle_count: number;
        head_battle_rate: number;
        in_battle_count: number;
        in_battle_rate: number;
        in_battle_win_count: number;
        in_battle_win_rate: number;
        in_team_count: number;
        in_team_rate: number;
        pokemon_name: string;
      }) => ({
        ...summary,
        head_battle_count: Number(summary.head_battle_count),
        head_battle_rate: Number(summary.head_battle_rate),
        in_battle_count: Number(summary.in_battle_count),
        in_battle_rate: Number(summary.in_battle_rate),
        in_battle_win_count: Number(summary.in_battle_win_count),
        in_battle_win_rate: Number(summary.in_battle_win_rate),
        in_team_count: Number(summary.in_team_count),
        in_team_rate: Number(summary.in_team_rate),
      })),
    },
  };
};

const Analytics: React.FC<AnalyticsProps> = ({ win_rates, next_ranks, your_pokemon_summary_result }) => {
  return (
    <Box bg="gray.50" minH="100vh">
      <Container maxW="container.xl" py="8">
        <HStack spacing={0}>
          <Heading padding={'5px'}>ログ分析</Heading>
          <Image src="./goodra.png" alt="goodra" boxSize="50px" />
        </HStack>
        <Box flex="1" p="4" bg="white">
          <SimpleGrid columns={2} spacing={10}>
            <TransitionChart
              data={win_rates}
              chartTitle={'勝率推移(シーズン3)'}
              dataLabel={'勝率'}
              dataColor={'rgb(255, 99, 132)'}
              dataBackGroundColor={'rgba(255, 99, 132, 0.5)'}
            />
            <TransitionChart
              data={next_ranks}
              chartTitle={'順位推移(シーズン3)'}
              dataLabel={'順位'}
              dataColor={'rgb(53, 162, 235)'}
              dataBackGroundColor={'rgba(53, 162, 235, 0.5)'}
            />
          </SimpleGrid>
          <Divider marginY={'10px'}/>
          <Heading size='md' padding={'10px'}>サマリー: 自分のポケモン</Heading>
          <Table>
              <Thead>
                <Tr>
                  <Th>ポケモン名</Th>
                  <Th>採用率</Th>
                  <Th>選出率</Th>
                  <Th>先発での選出率</Th>
                  <Th>選出されたときの勝率</Th>
                </Tr>
              </Thead>
              <Tbody>
                {your_pokemon_summary_result.map((summary) => (
                  <Tr key={summary.pokemon_name}>
                    <Td>{summary.pokemon_name}</Td>
                    <Td>{summary.in_team_rate.toFixed(4)}</Td>
                    <Td>{summary.in_battle_rate.toFixed(4)}</Td>
                    <Td>{summary.head_battle_rate.toFixed(4)}</Td>
                    <Td>{summary.in_battle_win_rate.toFixed(4)}</Td>
                  </Tr>
                ))}
              </Tbody>
            </Table>
        </Box>
      </Container>
    </Box>
  );
};

export default Analytics;
