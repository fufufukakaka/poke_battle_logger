import type { NextApiRequest, NextApiResponse } from 'next'
import axios from 'axios'
import { ServerHost } from '../../util'

const getVideoProcessStatus = async (req: NextApiRequest, res: NextApiResponse) => {
  const { trainerId } = req.query
  const results = await axios.get(`${ServerHost}/api/v1/get_battle_video_status_list?trainer_id=${trainerId}`);
  return res.status(200).json(results.data)
}

export default getVideoProcessStatus
