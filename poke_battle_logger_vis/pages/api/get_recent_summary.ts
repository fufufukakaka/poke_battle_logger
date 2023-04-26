import type { NextApiRequest, NextApiResponse } from 'next'
import axios from "axios"
import { ServerHost } from '../../util'

const getRecentSummaryHandler = async () => {
  const results = await axios.get(`${ServerHost}/api/v1/recent_battle_summary`);
  return results.data
}

export default getRecentSummaryHandler
