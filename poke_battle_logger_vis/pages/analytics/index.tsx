import {
  HStack,
  Image,
  Box,
  Container,
  Divider,
  SimpleGrid,
  Heading,
  Radio,
  RadioGroup,
  Stack,
} from '@chakra-ui/react';
import { Tabs, TabList, TabPanels, Tab, TabPanel } from '@chakra-ui/react'
import TransitionChart from '../../components/data-display/transition-chart';
import useSWR from 'swr';
import axios from 'axios';
import { useContext, useState } from 'react';
import { SeasonContext } from '../_app';
import { PokemonSelectionDataTable } from '@/components/data-display/pokemon-selection-data-table';
import { PokemonKnockOutDataTable } from '@/components/data-display/pokemon-knock-out-data-table';
import { createColumnHelper } from "@tanstack/react-table";
import { useAuth0, withAuthenticationRequired } from '@auth0/auth0-react';
import { ServerHost } from "../../util"


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
    yourPokemonKnockOutSummary:
      results.data.yourPokemonKnockOutSummary.map(
        (summary: {
          knock_out_count: number;
          your_pokemon_name: string;
          opponent_pokemon_name: string;
        }) => ({
          ...summary,
          knock_out_count: Number(summary.knock_out_count),
        })
      ),
    opponentPokemonKnockOutSummary:
      results.data.opponentPokemonKnockOutSummary.map(
        (summary: {
          knock_out_count: number;
          your_pokemon_name: string;
          opponent_pokemon_name: string;
        }) => ({
          ...summary,
          knock_out_count: Number(summary.knock_out_count),
        })
      ),
  };
};

type PokemonStat = {
  pokemon_name: string;
  in_team_rate: number;
  in_battle_rate: number;
  head_battle_rate: number;
  in_battle_win_rate: number;
  in_battle_lose_rate: number;
};

type PokemonKnockOutStat = {
  knock_out_count: number;
  your_pokemon_name: string;
  opponent_pokemon_name: string;
};

const yourPokemonStatsColumnHelper = createColumnHelper<PokemonStat>();
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

const opponentPokemonStatsColumnHelper = createColumnHelper<PokemonStat>();
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

const yourPokemonKnockOutStatsColumnHelper = createColumnHelper<PokemonKnockOutStat>();
const yourPokemonKnockOutStatsColumns = [
  yourPokemonKnockOutStatsColumnHelper.accessor("your_pokemon_name", {
    cell: (info) => info.getValue(),
    header: "自分のポケモン"
  }),
  yourPokemonKnockOutStatsColumnHelper.accessor("opponent_pokemon_name", {
    cell: (info) => info.getValue(),
    header: "倒した相手のポケモン"
  }),
  yourPokemonKnockOutStatsColumnHelper.accessor("knock_out_count", {
    cell: (info) => info.getValue(),
    header: "倒した数",
    meta: {
      isNumeric: true
    }
  })
];

const opponentPokemonKnockOutStatsColumnHelper = createColumnHelper<PokemonKnockOutStat>();
const opponentPokemonKnockOutStatsColumns = [
  opponentPokemonKnockOutStatsColumnHelper.accessor("your_pokemon_name", {
    cell: (info) => info.getValue(),
    header: "自分のポケモン"
  }),
  opponentPokemonKnockOutStatsColumnHelper.accessor("opponent_pokemon_name", {
    cell: (info) => info.getValue(),
    header: "倒された相手のポケモン"
  }),
  opponentPokemonKnockOutStatsColumnHelper.accessor("knock_out_count", {
    cell: (info) => info.getValue(),
    header: "倒された数",
    meta: {
      isNumeric: true
    }
  })
];

const Analytics: React.FC = () => {
  const { user } = useAuth0();
  const season = useContext(SeasonContext);
  const { data, error, isLoading } = useSWR(
    `${ServerHost}/api/v1/analytics?season=${season}&trainer_id=${user?.sub?.replace("|", "_")}`,
    fetcher
  )
  const [selectedValue, setSelectedValue] = useState('1')

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
          <RadioGroup onChange={setSelectedValue} value={selectedValue}>
            <Stack direction='row'>
              <Radio value='1'>Selection Count</Radio>
              <Radio value='2'>KnockOut Count</Radio>
            </Stack>
          </RadioGroup>
          {selectedValue === '1' ? (
            <Heading size="md" padding={'10px'}>
              選出ログサマリー
            </Heading>)
            : selectedValue === '2' ? (
              <Heading size="md" padding={'10px'}>
                ノックアウトログサマリー
              </Heading>
            ) : null
          }
          {selectedValue === '1' ? (
          <Tabs>
            <TabList>
              <Tab>自分のポケモン</Tab>
              <Tab>相手のポケモン</Tab>
            </TabList>
            <TabPanels>
              <TabPanel>
                <PokemonSelectionDataTable columns={yourPokemonStatsColumns} data={data.yourPokemonStatsSummary} />
              </TabPanel>
              <TabPanel>
                <PokemonSelectionDataTable columns={opponentPokemonStatsColumns} data={data.opponentPokemonStatsSummary} />
              </TabPanel>
            </TabPanels>
          </Tabs> ) : selectedValue === '2' ? (
            <Tabs>
              <TabList>
                <Tab>自分のポケモン</Tab>
                <Tab>相手のポケモン</Tab>
              </TabList>
              <TabPanels>
                <TabPanel>
                  <PokemonKnockOutDataTable columns={yourPokemonKnockOutStatsColumns} data={data.yourPokemonKnockOutSummary} />
                </TabPanel>
                <TabPanel>
                  <PokemonKnockOutDataTable columns={opponentPokemonKnockOutStatsColumns} data={data.opponentPokemonKnockOutSummary} />
                </TabPanel>
              </TabPanels>
            </Tabs>) : null
          }
        </Box>
      </Container>
    </Box>
  );
};

export default withAuthenticationRequired(Analytics);
