import { Card, CardHeader, CardBody, SimpleGrid, Heading, Text } from '@chakra-ui/react'
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
        <SimpleGrid spacing={10} templateColumns='repeat(auto-fill, minmax(200px, 1fr))'>
        <Card>
          <CardHeader>
            <Heading size='md'>{'εη π'}</Heading>
          </CardHeader>
          <CardBody>
            <Text fontSize='2xl'>{win_rate * 100}%</Text>
          </CardBody>
        </Card>
        <Card>
          <CardHeader>
            <Heading size='md'>{'ι δ½ π'}</Heading>
          </CardHeader>
          <CardBody>
            <Text fontSize='2xl'>{latest_rank}</Text>
          </CardBody>
        </Card>
        <Card>
          <CardHeader>
            <Heading size='md'>{'ζθΏεγ£γγγ±γ’γ³ β­'}</Heading>
          </CardHeader>
          <CardBody>
            <Text fontSize='2xl'>{latest_win_pokemon}</Text>
            <Image src={latest_win_pokemon_image} alt={latest_win_pokemon} />
          </CardBody>
        </Card>
        <Card>
          <CardHeader>
            <Heading size='md'>{'ζθΏθ² γγγγ±γ’γ³ β'}</Heading>
          </CardHeader>
          <CardBody>
            <Text fontSize='2xl'>{latest_lose_pokemon}</Text>
            <Image src={latest_lose_pokemon_image} alt={latest_lose_pokemon} />
          </CardBody>
        </Card>
      </SimpleGrid>
    );
  };
  
  export default PokeStatGroup;
  