import axios from "axios";
import type { NextApiRequest, NextApiResponse } from "next";
import { ServerHost } from '../../util'

const handler = async (req: NextApiRequest, res: NextApiResponse) => {
  if (req.method === "POST") {
    try {
      const response = await axios.post(`${ServerHost}/api/v1/set_label_to_unknown_pokemon_images`, req.body);
      res.status(200).json(response.data);
    } catch (error) {
      console.error("Error proxying request:", error);
      res.status(500).json({ error: "Error proxying request" });
    }
  } else {
    res.status(405).json({ error: "Method not allowed" });
  }
};

export default handler;
