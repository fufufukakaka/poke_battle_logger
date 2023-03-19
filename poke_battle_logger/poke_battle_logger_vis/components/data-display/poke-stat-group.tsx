import {
  Card,
  CardHeader,
  CardBody,
  SimpleGrid,
  Heading,
  Text,
} from '@chakra-ui/react';
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
    <SimpleGrid
      spacing={10}
      templateColumns="repeat(auto-fill, minmax(200px, 1fr))"
    >
      <Card>
        <CardHeader>
          <Heading size="md">{'勝率 👊'}</Heading>
        </CardHeader>
        <CardBody>
          <Text fontSize="2xl">{win_rate * 100}%</Text>
        </CardBody>
      </Card>
      <Card>
        <CardHeader>
          <Heading size="md">{'順位 👑'}</Heading>
        </CardHeader>
        <CardBody>
          <Text fontSize="2xl">{latest_rank}</Text>
        </CardBody>
      </Card>
      <Card>
        <CardHeader>
          <Heading size="md">{'最近勝ったポケモン ⭕'}</Heading>
        </CardHeader>
        <CardBody>
          <Text fontSize="2xl">{latest_win_pokemon}</Text>
          <PokemonIcon pokemon_name={latest_win_pokemon} />
        </CardBody>
      </Card>
      <Card>
        <CardHeader>
          <Heading size="md">{'最近負けたポケモン ❎'}</Heading>
        </CardHeader>
        <CardBody>
          <Text fontSize="2xl">{latest_lose_pokemon}</Text>
          <PokemonIcon pokemon_name={latest_lose_pokemon} />
        </CardBody>
      </Card>
    </SimpleGrid>
  );
};

export default PokeStatGroup;
