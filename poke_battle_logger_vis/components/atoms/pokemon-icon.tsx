import { Image, Skeleton } from '@chakra-ui/react';
import axios from 'axios';
import useSWR from 'swr';

interface PokemonIconProps {
  pokemon_name: string;
  boxSize: string;
}

const fetcher = async (url: string) => {
  const result = await axios.get(url);
  return await result.data;
};

const PokemonIcon: React.FC<PokemonIconProps> = ({ pokemon_name, boxSize }) => {
  const { data, error, isLoading } = useSWR(
    'http://127.0.0.1:8000/api/v1/pokemon_image_url?pokemon_name=' +
      pokemon_name,
    fetcher
  );
  if (isLoading) return <Skeleton />;
  if (error) return <Skeleton />;
  if (!data) return <Skeleton />;

  return (
    <Image src={data} alt={pokemon_name} boxSize={boxSize} align={'center'}/>
  );
};

export default PokemonIcon;
