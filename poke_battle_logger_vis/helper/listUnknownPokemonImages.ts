// helper/listUnknownPokemonImages.ts
import { Storage } from '@google-cloud/storage';

const storage = new Storage();
const bucketName = 'poke_battle_logger_templates';
const prefix = 'pokemon_templates/users/1/unknown_pokemon_templates/';

export const listUnknownPokemonImages = async () => {
  const options = {
    prefix: prefix,
    delimiter: '/',
  };

  const [files] = await storage.bucket(bucketName).getFiles(options);

  const imageFiles = files.filter(file => file.name.endsWith('.png'));
  return imageFiles.map(file => file.name);
}
