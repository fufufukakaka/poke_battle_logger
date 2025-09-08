import { Card, CardHeader, CardContent, CardTitle } from '@/components/ui/card';
import PokemonIcon from '@/components/atoms/pokemon-icon';

interface PokeStatGroupProps {
  latest_lose_pokemon: string;
  latest_rank: number;
  latest_win_pokemon: string;
  win_rate: number;
}

const PokeStatGroup: React.FunctionComponent<PokeStatGroupProps> = ({
  latest_lose_pokemon,
  latest_rank,
  latest_win_pokemon,
  win_rate,
}) => {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">勝率 👊</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-2xl font-bold">{(win_rate * 100).toFixed(1)}%</p>
        </CardContent>
      </Card>
      
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">順位 👑</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-2xl font-bold">{latest_rank}</p>
        </CardContent>
      </Card>
      
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">最近勝ったポケモン ⭕</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-2xl font-bold mb-2">{latest_win_pokemon}</p>
          <PokemonIcon pokemon_name={latest_win_pokemon} boxSize={"150px"} />
        </CardContent>
      </Card>
      
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">最近負けたポケモン ❎</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-2xl font-bold mb-2">{latest_lose_pokemon}</p>
          <PokemonIcon pokemon_name={latest_lose_pokemon} boxSize={"150px"} />
        </CardContent>
      </Card>
    </div>
  );
};

export default PokeStatGroup;
