import type { NextApiRequest, NextApiResponse } from 'next';
import { getImageURLFromGCS } from '../../helper/getImageURLFromGCS'

const handler = async (req: NextApiRequest, res: NextApiResponse) => {
  const { fileName } = req.query;

  if (!fileName) {
    res.status(400).json({ message: 'File name is required' });
    return;
  }

  try {
    const url = await getImageURLFromGCS(fileName as string);
    res.status(200).json({ url });
  } catch (error) {
    console.error('Error getting image URL:', error);
    res.status(500).json({ message: 'Error getting image URL' });
  }
}

export default handler
