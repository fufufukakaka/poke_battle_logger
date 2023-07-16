import type { NextApiRequest, NextApiResponse } from 'next'
import axios from "axios"
import { ServerHost } from '../../util'

const getInBattleFaintedLogHandler = async (req: NextApiRequest, res: NextApiResponse) => {
  const results = await axios.get(`${ServerHost}/api/v1/fainted_pokemon_log?battle_id=${req.query.battle_id}`);
  const { data } = results
  return res.status(200).json(data)
}

export default getInBattleFaintedLogHandler
