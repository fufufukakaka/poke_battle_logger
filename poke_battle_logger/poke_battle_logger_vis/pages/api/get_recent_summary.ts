import type { NextApiRequest, NextApiResponse } from 'next'
import axios from "axios"

const handler = async (req: NextApiRequest, res: NextApiResponse) => {
  const results = await axios.get("http://127.0.0.1:8000/api/v1/recent_battle_summary");
  res.status(200).json(results.data)
}

export default handler
