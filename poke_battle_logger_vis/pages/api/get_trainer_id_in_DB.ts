import type { NextApiRequest, NextApiResponse } from 'next'
import axios from 'axios'
import { ServerHost } from '../../util'

const getTrainerIdInDB = async (req: NextApiRequest, res: NextApiResponse) => {
  const { trainerId } = req.query
  const results = await axios.get(`${ServerHost}/api/v1/get_trainer_id_in_DB?trainer_id=${trainerId}`);
  return res.status(200).json(results.data)
}

export default getTrainerIdInDB
