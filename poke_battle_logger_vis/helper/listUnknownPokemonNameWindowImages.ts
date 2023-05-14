// helper/listUnknownPokemonNameWindowImages.ts
import { Storage } from '@google-cloud/storage';

const storage = new Storage();
const bucketName = 'poke_battle_logger_templates';

export const listUnknownPokemonNameWindowImages = async (trainer_id: number) => {
  const options = {
    prefix: `pokemon_name_window_templates/users/${trainer_id}/unknown_pokemon_name_window_templates/`,
    delimiter: '/',
  };

  const [files] = await storage.bucket(bucketName).getFiles(options);

  const imageFiles = files.filter(file => file.name.endsWith('.png'));
  return imageFiles.map(file => file.name);
}
