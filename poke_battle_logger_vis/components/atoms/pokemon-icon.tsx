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
  // オーガポン系、イイネイヌ系など新ポケモンは画像がないので Unseen 画像を出す
//   10035,炎オーガポン,Ogerpon Hearthflame
// 10035,岩オーガポン,Ogerpon Cornerstone
// 10035,水オーガポン,Ogerpon Wellspring
  const newPokemonList = [
    "カミッチュ",
    "チャデス",
    "ヤバソチャ",
    "イイネイヌ",
    "マシマシラ",
    "キチキギス",
    "オーガポン",
    "炎オーガポン",
    "岩オーガポン",
    "水オーガポン"
  ]
  // if newPokemonList includes pokemon_name, return unseen image
  if (newPokemonList.includes(pokemon_name)) {
    return "https://upload.wikimedia.org/wikipedia/commons/5/53/Pok%C3%A9_Ball_icon.svg";
  }
  return `https://img.pokemondb.net/sprites/scarlet-violet/normal/${pokemon_name}.png`;
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
