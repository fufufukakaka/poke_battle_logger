export const getImageUrlClient = async (fileName: string): Promise<string> => {
    const response = await fetch(`/api/getImageUrl?fileName=${fileName}`);

    if (!response.ok) {
      throw new Error('Error getting image URL');
    }

    const data = await response.json();
    return data.url;
  };
