import type { NextApiRequest, NextApiResponse } from 'next'
import axios from "axios"
import { ServerHost } from '../../util'


const getCheckVideoFormatHandler = async (req: NextApiRequest, res: NextApiResponse) => {
  const { videoId } = req.query
  const results = await axios.get(`${ServerHost}/api/v1/check_video_format?video_id=${videoId}`);
  return res.status(200).json(results.data)
}

export default getCheckVideoFormatHandler
