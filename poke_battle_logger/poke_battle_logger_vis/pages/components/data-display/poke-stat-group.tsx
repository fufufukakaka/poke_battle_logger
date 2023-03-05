import {
  Stat,
  StatLabel,
  StatNumber,
  StatGroup,
} from '@chakra-ui/react';
import { Image } from '@chakra-ui/react'

interface PokeStatGroupProps {
  latest_lose_pokemon: string
  latest_lose_pokemon_image: string
  latest_rank: number
  latest_win_pokemon: string
  latest_win_pokemon_image: string
  win_rate: number
}

const PokeStatGroup: React.FunctionComponent<PokeStatGroupProps> = ({
  latest_lose_pokemon,
  latest_lose_pokemon_image,
  latest_rank,
  latest_win_pokemon,
  latest_win_pokemon_image,
  win_rate,
}) => {
  return (
    <>
      <StatGroup>
        <Stat px={{ base: 4, md: 8 }} py={'5'} shadow={'s'} rounded={'lg'}>
          <StatLabel fontWeight={'medium'}>勝率 👊</StatLabel>
          <StatNumber>{win_rate * 100}%</StatNumber>
        </Stat>
        <Stat px={{ base: 4, md: 8 }} py={'5'} shadow={'s'} rounded={'lg'}>
          <StatLabel fontWeight={'medium'}>順位 👑</StatLabel>
          <StatNumber>{latest_rank}</StatNumber>
        </Stat>
        <Stat px={{ base: 4, md: 8 }} py={'5'} shadow={'s'} rounded={'lg'}>
          <StatLabel fontWeight={'medium'}>最近勝ったポケモン ⭕</StatLabel>
          <StatNumber>{latest_win_pokemon}</StatNumber>
          <Image src={latest_win_pokemon_image} alt={latest_win_pokemon} />
        </Stat>
        <Stat px={{ base: 4, md: 8 }} py={'5'} shadow={'s'} rounded={'lg'}>
          <StatLabel fontWeight={'medium'}>最近負けたポケモン ❎</StatLabel>
          <StatNumber>{latest_lose_pokemon}</StatNumber>
          <Image src={latest_lose_pokemon_image} alt={latest_lose_pokemon} />
        </Stat>
      </StatGroup>
    </>
  );
};

export default PokeStatGroup;
