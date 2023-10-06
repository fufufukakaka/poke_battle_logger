import { Image } from '@chakra-ui/react';
import { pokemonJapaneseToEnglishDict } from '../../helper/pokemonJapaneseToEnglishDict'

interface PokemonIconProps {
  pokemon_name: string;
  boxSize: string;
}

const getPokemonImageUrl = (pokemon_name: string) => {
  pokemon_name = pokemon_name.normalize("NFC");
  if (pokemon_name === "Unseen") {
    return "https://upload.wikimedia.org/wikipedia/commons/5/53/Pok%C3%A9_Ball_icon.svg";
  }
  if (pokemon_name in pokemonJapaneseToEnglishDict) {
    pokemon_name = pokemonJapaneseToEnglishDict[pokemon_name];
  }
  pokemon_name = pokemon_name.toLowerCase().replaceAll(" ", "-");
  return `https://poke-battle-logger-sprites.com/sprites/${pokemon_name}.png`;
};

const PokemonIcon: React.FC<PokemonIconProps> = ({ pokemon_name, boxSize }) => {
  return (
    <Image
      src={getPokemonImageUrl(pokemon_name)}
      alt={pokemon_name}
      boxSize={boxSize}
      align={'center'}
    />
  );
};

export default PokemonIcon;
