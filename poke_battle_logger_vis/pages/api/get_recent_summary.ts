import type { NextApiRequest, NextApiResponse } from 'next'
import axios from "axios"

const getRecentSummaryHandler = async () => {
  const results = await axios.get("http://127.0.0.1:8000/api/v1/recent_battle_summary");
  return results.data
}

export default getRecentSummaryHandler
