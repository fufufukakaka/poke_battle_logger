import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent } from '@/components/ui/card';
import { Separator } from '@/components/ui/separator';
import { Loader } from 'lucide-react';
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
    if (isAuthenticated && user && user.sub && user.email) {
      axios.post(`${ServerHost}/api/v1/save_new_trainer`, {
        trainer_id: user.sub.replace("|", "_"),
        trainer_email: user.email,
    })
  }}, [isAuthenticated, user])


  if (isLoading) return (
    <div className="flex items-center justify-center h-64">
      <Loader className="animate-spin h-8 w-8" />
    </div>
  )
  if (error) return <p>error</p>
  if (!data) return <p>no data</p>

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto py-8">
        <h1 className="text-3xl font-bold p-2 mb-4">ダッシュボード</h1>
        <Card>
          <CardContent className="p-6">
            <div className="space-y-6">
              <PokeStatGroup
                latest_lose_pokemon={data.latest_lose_pokemon}
                latest_rank={data.latest_rank}
                latest_win_pokemon={data.latest_win_pokemon}
                win_rate={Number(data.win_rate.toFixed(4))}
              />
              <Separator />
              <h2 className="text-xl font-semibold p-2">活動履歴</h2>
              <div className="overflow-x-auto">
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
              </div>
              <Separator />
              <h2 className="text-xl font-semibold p-2">
                最近の対戦履歴
              </h2>
              <div className="rounded-md border">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>対戦ID</TableHead>
                      <TableHead>対戦日時</TableHead>
                      <TableHead>勝敗</TableHead>
                      <TableHead>順位</TableHead>
                      <TableHead>自分の初手</TableHead>
                      <TableHead>相手の初手</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {data.recent_battle_history.map((battle) => (
                      <TableRow key={battle.battle_id}>
                        <TableCell>{battle.battle_id}</TableCell>
                        <TableCell>{battle.created_at}</TableCell>
                        <TableCell>
                          {battle.win_or_lose === 'win' ? (
                            <Badge className="bg-green-100 text-green-800 hover:bg-green-100">勝利！</Badge>
                          ) : (
                            <Badge className="bg-red-100 text-red-800 hover:bg-red-100">負け</Badge>
                          )}
                        </TableCell>
                        <TableCell>{battle.next_rank}</TableCell>
                        <TableCell>{battle.your_pokemon_1}</TableCell>
                        <TableCell>{battle.opponent_pokemon_1}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

// このページは認証が必要なため、SSGではなくSSRを使用
export async function getServerSideProps() {
  // 認証が必要なページなので、常に動的レンダリング
  return {
    props: {}
  };
}

export default withAuthenticationRequired(Dashboard);
