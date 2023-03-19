import {
  Card,
  CardHeader,
  CardBody,
  SimpleGrid,
  Heading,
  Text,
  Badge,
  Divider,
} from '@chakra-ui/react';
import {TimeIcon} from '@chakra-ui/icons';

interface BattleLogCardProps {
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
}

const BattleLogCard: React.FunctionComponent<BattleLogCardProps> = ({
  battle_id,
  battle_created_at,
  win_or_lose,
  next_rank,
  your_pokemon_team,
  opponent_pokemon_team,
  your_pokemon_select1,
  your_pokemon_select2,
  your_pokemon_select3,
  opponent_pokemon_select1,
  opponent_pokemon_select2,
  opponent_pokemon_select3,
}) => {
  return (
    <Card>
      <CardBody>
        <Text><TimeIcon boxSize={4} margin={"5px"} />{battle_created_at}</Text>
        <Text>
          {win_or_lose === 'win' ? (
            <Badge colorScheme="green">勝利！</Badge>
          ) : (
            <Badge colorScheme="red">負け</Badge>
          )} → 👑 {next_rank}
        </Text>
        <Divider margin={"5px"}/>
        <Text>あなたのポケモンチーム: {your_pokemon_team}</Text>
        <Text>相手のポケモンチーム: {opponent_pokemon_team}</Text>
        <Text>あなたのポケモン1: {your_pokemon_select1}</Text>
        <Text>あなたのポケモン2: {your_pokemon_select2}</Text>
        <Text>あなたのポケモン3: {your_pokemon_select3}</Text>
        <Text>相手のポケモン1: {opponent_pokemon_select1}</Text>
        <Text>相手のポケモン2: {opponent_pokemon_select2}</Text>
        <Text>相手のポケモン3: {opponent_pokemon_select3}</Text>
      </CardBody>
    </Card>
  );
};

export default BattleLogCard;
