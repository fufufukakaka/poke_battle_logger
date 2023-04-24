import type { NextApiRequest, NextApiResponse } from 'next'
import axios from "axios"

const getCheckVideoFormatHandler = async (req: NextApiRequest, res: NextApiResponse) => {
  const { videoId } = req.query
  const results = await axios.get(`http://127.0.0.1:8000/api/v1/check_video_format?video_id=${videoId}`);
  return res.status(200).json(results.data)
}

export default getCheckVideoFormatHandler
