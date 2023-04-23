import type { NextApiRequest, NextApiResponse } from 'next'
import axios from "axios"

const getWinRateTransitionHandler = async () => {
  const results = await axios.get("http://127.0.0.1:8000/api/v1/win_rate_transition?season=3");
  return {"data": results.data}
}

export default getWinRateTransitionHandler
