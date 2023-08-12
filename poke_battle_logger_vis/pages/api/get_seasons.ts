import type { NextApiRequest, NextApiResponse } from 'next'
import axios from 'axios'
import { ServerHost } from '../../util'

const getSeasons = async (req: NextApiRequest, res: NextApiResponse) => {
  const results = await axios.get(`${ServerHost}/api/v1/get_seasons`);
  return res.status(200).json(results.data)
}

export default getSeasons
