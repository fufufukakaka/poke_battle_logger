import type { NextApiRequest, NextApiResponse } from 'next'
import axios from "axios"

const getOpponentPokemonSummaryHandler = async () => {
  const results = await axios.get("http://127.0.0.1:8000/api/v1/opponent_pokemon_stats_summary?season=3");
  return {"data": results.data}
}

export default getOpponentPokemonSummaryHandler
