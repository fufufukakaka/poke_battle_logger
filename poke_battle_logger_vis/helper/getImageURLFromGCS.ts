import { Storage } from '@google-cloud/storage';

const storage = new Storage();
const bucketName = 'poke_battle_logger_templates';

export const getImageURLFromGCS = async (fileName: string): Promise<string> => {
  const options = {
    version: 'v4' as const,
    action: 'read' as const,
    expires: Date.now() + 1000 * 60 * 60, // 1hour
  };

  const url = await storage.bucket(bucketName).file(fileName).getSignedUrl(options);
  return url as unknown as string;
};
