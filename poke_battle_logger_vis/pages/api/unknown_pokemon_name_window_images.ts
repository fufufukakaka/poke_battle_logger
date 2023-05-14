// pages/api/unknown_pokemon_images.ts
import type { NextApiRequest, NextApiResponse } from 'next'
import { listUnknownPokemonNameWindowImages } from '../../helper/listUnknownPokemonNameWindowImages'

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  const imageList = await listUnknownPokemonNameWindowImages(Number(req.query.trainer_id));
  res.status(200).json({ imageList });
}
