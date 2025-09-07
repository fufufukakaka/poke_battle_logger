import { cn } from '@/lib/utils';
import { pokemonJapaneseToEnglishDict } from '../../helper/pokemonJapaneseToEnglishDict';

interface PokemonIconProps {
  pokemon_name: string;
  boxSize: string;
  className?: string;
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

const PokemonIcon: React.FC<PokemonIconProps> = ({ pokemon_name, boxSize, className }) => {
  const sizeClasses = boxSize === "150px" ? "w-[150px] h-[150px]" : 
                     boxSize === "50px" ? "w-10 h-10" :
                     boxSize === "40px" ? "w-8 h-8" :
                     `w-[${boxSize}] h-[${boxSize}]`;
  
  return (
    <img
      src={getPokemonImageUrl(pokemon_name)}
      alt={pokemon_name}
      className={cn(sizeClasses, "object-contain", className)}
    />
  );
};

export default PokemonIcon;
