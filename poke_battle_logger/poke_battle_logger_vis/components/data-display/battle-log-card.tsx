import {
  Card,
  CardHeader,
  CardBody,
  SimpleGrid,
  Flex,
  Text,
  Badge,
  Divider,
} from '@chakra-ui/react';
import { TimeIcon } from '@chakra-ui/icons';
import PokemonIcon from '../atoms/pokemon-icon';

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
        <Text>
          <TimeIcon boxSize={4} margin={'5px'} />
          {battle_created_at}
        </Text>
        <Text>
          {win_or_lose === 'win' ? (
            <Badge colorScheme="green">勝利！</Badge>
          ) : (
            <Badge colorScheme="red">負け</Badge>
          )}{' '}
          → 👑 {next_rank}
        </Text>
        <Divider margin={'5px'} />
        <Text>ShowDown</Text>
        <Flex>
          {
            your_pokemon_team.split(',').map((pokemon_name) => (
              <PokemonIcon key={pokemon_name} pokemon_name={pokemon_name} boxSize={'40px'} />
            ))
          }
        </Flex>
        <Text>VS</Text>
        <Flex>
          {
            opponent_pokemon_team.split(',').map((pokemon_name) => (
              <PokemonIcon key={pokemon_name} pokemon_name={pokemon_name} boxSize={'40px'} />
            ))
          }
        </Flex>
        <Divider margin={'5px'} />
        <Text>Selection</Text>
        <Flex>
          <PokemonIcon pokemon_name={your_pokemon_select1} boxSize={'50px'} />
          <PokemonIcon pokemon_name={your_pokemon_select2} boxSize={'50px'} />
          <PokemonIcon pokemon_name={your_pokemon_select3} boxSize={'50px'} />
        </Flex>
        <Text>VS</Text>
        <Flex>
          <PokemonIcon
            pokemon_name={opponent_pokemon_select1}
            boxSize={'50px'}
          />
          <PokemonIcon
            pokemon_name={opponent_pokemon_select2}
            boxSize={'50px'}
          />
          <PokemonIcon
            pokemon_name={opponent_pokemon_select3}
            boxSize={'50px'}
          />
        </Flex>
      </CardBody>
    </Card>
  );
};

export default BattleLogCard;
