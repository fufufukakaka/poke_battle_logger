// pages/api/unknown_pokemon_images.ts
import type { NextApiRequest, NextApiResponse } from 'next'
import { listUnknownPokemonImages } from '../../helper/listUnknownPokemonImages'

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  const imageList = await listUnknownPokemonImages(Number(req.query.trainer_id));
  res.status(200).json({ imageList });
}
