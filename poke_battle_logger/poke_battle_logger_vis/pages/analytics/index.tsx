import {
  HStack,
  Image,
  Box,
  Container,
  Divider,
  SimpleGrid,
  Heading,
} from '@chakra-ui/react';
import { Tabs, TabList, TabPanels, Tab, TabPanel } from '@chakra-ui/react'
import TransitionChart from '../../components/data-display/transition-chart';
import useSWR from 'swr';
import axios from 'axios';
import { useContext } from 'react';
import { SeasonContext } from '../_app';
import { DataTable } from '@/components/data-display/data-table';
import { createColumnHelper } from "@tanstack/react-table";
import { withAuthenticationRequired } from '@auth0/auth0-react';

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

const fetcher = async (url: string) => {
  const results = await axios.get(url);
  return await {
    winRates: results.data.winRate,
    nextRanks: results.data.nextRank,
    // convert to number
    yourPokemonStatsSummary: results.data.yourPokemonStatsSummary.map(
      (summary: {
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
        head_battle_rate: Number(summary.head_battle_rate).toFixed(3),
        in_battle_count: Number(summary.in_battle_count),
        in_battle_rate: Number(summary.in_battle_rate).toFixed(3),
        in_battle_win_count: Number(summary.in_battle_win_count),
        in_battle_win_rate: Number(summary.in_battle_win_rate).toFixed(3),
        in_team_count: Number(summary.in_team_count),
        in_team_rate: Number(summary.in_team_rate).toFixed(3),
      })
    ),
    // convert to number
    opponentPokemonStatsSummary:
      results.data.opponentPokemonStatsSummary.map(
        (summary: {
          head_battle_count: number;
          head_battle_rate: number;
          in_battle_count: number;
          in_battle_rate: number;
          in_battle_lose_count: number;
          in_battle_lose_rate: number;
          in_team_count: number;
          in_team_rate: number;
          pokemon_name: string;
        }) => ({
          ...summary,
          head_battle_count: Number(summary.head_battle_count),
          head_battle_rate: Number(summary.head_battle_rate).toFixed(3),
          in_battle_count: Number(summary.in_battle_count),
          in_battle_rate: Number(summary.in_battle_rate).toFixed(3),
          in_battle_losecount: Number(summary.in_battle_lose_count),
          in_battle_lose_rate: Number(summary.in_battle_lose_rate).toFixed(3),
          in_team_count: Number(summary.in_team_count),
          in_team_rate: Number(summary.in_team_rate).toFixed(3),
        })
      ),
  };
};

type YourPokemonStat = {
  pokemon_name: string;
  in_team_rate: number;
  in_battle_rate: number;
  head_battle_rate: number;
  in_battle_win_rate: number;
};

type OpponentPokemonStat = {
  pokemon_name: string;
  in_team_rate: number;
  in_battle_rate: number;
  head_battle_rate: number;
  in_battle_lose_rate: number;
};

const yourPokemonStatsColumnHelper = createColumnHelper<YourPokemonStat>();
const yourPokemonStatsColumns = [
  yourPokemonStatsColumnHelper.accessor("pokemon_name", {
    cell: (info) => info.getValue(),
    header: "ポケモン名"
  }),
  yourPokemonStatsColumnHelper.accessor("in_team_rate", {
    cell: (info) => info.getValue(),
    header: "採用率",
    meta: {
      isNumeric: true
    }
  }),
  yourPokemonStatsColumnHelper.accessor("in_battle_rate", {
    cell: (info) => info.getValue(),
    header: "選出率",
    meta: {
      isNumeric: true
    }
  }),
  yourPokemonStatsColumnHelper.accessor("head_battle_rate", {
    cell: (info) => info.getValue(),
    header: "選出したときの先発率",
    meta: {
      isNumeric: true
    }
  }),
  yourPokemonStatsColumnHelper.accessor("in_battle_win_rate", {
    cell: (info) => info.getValue(),
    header: "選出したときの勝率",
    meta: {
      isNumeric: true
    }
  })
];

const opponentPokemonStatsColumnHelper = createColumnHelper<OpponentPokemonStat>();
const opponentPokemonStatsColumns = [
  opponentPokemonStatsColumnHelper.accessor("pokemon_name", {
    cell: (info) => info.getValue(),
    header: "ポケモン名"
  }),
  opponentPokemonStatsColumnHelper.accessor("in_team_rate", {
    cell: (info) => info.getValue(),
    header: "遭遇率",
    meta: {
      isNumeric: true
    }
  }),
  opponentPokemonStatsColumnHelper.accessor("in_battle_rate", {
    cell: (info) => info.getValue(),
    header: "選出率",
    meta: {
      isNumeric: true
    }
  }),
  opponentPokemonStatsColumnHelper.accessor("head_battle_rate", {
    cell: (info) => info.getValue(),
    header: "選出されたときの先発率",
    meta: {
      isNumeric: true
    }
  }),
  opponentPokemonStatsColumnHelper.accessor("in_battle_lose_rate", {
    cell: (info) => info.getValue(),
    header: "選出されたときの負け率",
    meta: {
      isNumeric: true
    }
  })
];

const Analytics: React.FC<AnalyticsProps> = () => {
  const season = useContext(SeasonContext);
  const { data, error, isLoading } = useSWR(
    `http://127.0.0.1:8000/api/v1/analytics?season=${season}`,
    fetcher
  )

  if (isLoading) return <p>loading...</p>
  if (error) return <p>error</p>
  if (!data) return <p>no data</p>

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
              data={data.winRates}
              chartTitle={season === 0 ? `勝率推移(通算)` : `勝率推移(シーズン${season})`}
              dataLabel={'勝率'}
              dataColor={'rgb(255, 99, 132)'}
              dataBackGroundColor={'rgba(255, 99, 132, 0.5)'}
            />
            <TransitionChart
              data={data.nextRanks}
              chartTitle={season === 0 ? `順位推移(通算)` : `順位推移(シーズン${season})`}
              dataLabel={'順位'}
              dataColor={'rgb(53, 162, 235)'}
              dataBackGroundColor={'rgba(53, 162, 235, 0.5)'}
            />
          </SimpleGrid>
          <Divider marginY={'10px'} />
          <Heading size="md" padding={'10px'}>
            サマリー
          </Heading>
          <Tabs>
            <TabList>
              <Tab>自分のポケモン</Tab>
              <Tab>相手のポケモン</Tab>
            </TabList>
            <TabPanels>
              <TabPanel>
                <DataTable columns={yourPokemonStatsColumns} data={data.yourPokemonStatsSummary} />
              </TabPanel>
              <TabPanel>
                <DataTable columns={opponentPokemonStatsColumns} data={data.opponentPokemonStatsSummary} />
              </TabPanel>
            </TabPanels>
          </Tabs>
        </Box>
      </Container>
    </Box>
  );
};

export default withAuthenticationRequired(Analytics);
