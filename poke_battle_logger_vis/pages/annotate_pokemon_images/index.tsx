import React, { useState } from "react";
import { useAuth0, withAuthenticationRequired } from "@auth0/auth0-react";
import useSWR from "swr";
import { getImageUrlClient } from "@/helper/getImageURLClient";
import Select from 'react-select'
import { reactSelectOptions } from "@/helper/pokemonJapaneseToEnglishDict";
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';
import { useToast } from '@/components/ui/use-toast';


type Image = {
    fileName: string;
    url: string;
};

const fetcher = async (url: string) => {
    const res = await fetch(url);
    const data = await res.json();
    return data
}

const URLfetcher = async (url: string) => {
    const res = await fetch(url);
    const data = await res.json();
    const imageFileList = data.imageList as string[];

    const imageURLList = await Promise.all(
        imageFileList.map(async (fileName) => {
        const url = await getImageUrlClient(fileName);
        return url;
      })
    );

    return {imageURLList, imageFileList}
};

const AnnotatePokemonImagesPage = () => {
  const { user } = useAuth0();
  const trainerId = user?.sub?.replace("|", "_");
  const { data: dataTrainerIdInDB } = useSWR(`/api/get_trainer_id_in_DB?trainerId=${trainerId}`, fetcher);
  const trainerIdInDB = dataTrainerIdInDB;

  const { data, error } = useSWR(trainerIdInDB ? `/api/unknown_pokemon_images?trainer_id=${trainerIdInDB}` : null, URLfetcher);
  const imageDataList = data;
  const [imageLabels, setImageLabels] = useState<{ pokemon_image_file_on_gcs: string; pokemon_label: string; }[]>([]);

  const { data: nameWindowData, error: nameWindowError } = useSWR(trainerIdInDB ? `/api/unknown_pokemon_name_window_images?trainer_id=${trainerIdInDB}` : null, URLfetcher);
  const nameWindowImageDataList = nameWindowData;
  const [nameWindowImageLabels, setNameWindowImageLabels] = useState<{ pokemon_name_window_image_file_on_gcs: string; pokemon_name_window_label: string; }[]>([]);

  const { toast } = useToast();

  if (error || nameWindowError) return <div>Error loading images</div>;
  if (!imageDataList || !nameWindowImageDataList) return <div>Loading...</div>;

  const handleSelectChange = (index: number, option: any) => {
    const updatedLabels = [...imageLabels];
    updatedLabels[index] = {
      pokemon_image_file_on_gcs: imageDataList.imageFileList[index],
      pokemon_label: option.value,
    };
    setImageLabels(updatedLabels);
  };

  const handleSubmit = async () => {
    try {
      const response = await fetch("/api/set_label_to_unknown_pokemon_images", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          trainer_id: trainerIdInDB,
          image_labels: imageLabels,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        toast({
          title: "Success",
          description: data.message,
        });
      } else {
        const data = await response.json();
        throw new Error(data.detail);
      }
    } catch (error) {
      const typedError = error as any;
      toast({
        title: "Error",
        description: typedError.message,
        variant: "destructive",
      });
    }
  };

  const handleNameWindowSelectChange = (index: number, option: any) => {
    const updatedLabels = [...nameWindowImageLabels];
    updatedLabels[index] = {
      pokemon_name_window_image_file_on_gcs: nameWindowImageDataList.imageFileList[index],
      pokemon_name_window_label: option.value,
    };
    setNameWindowImageLabels(updatedLabels);
  };

  const handleNameWindowSubmit = async () => {
    try {
      const response = await fetch("/api/set_label_to_unknown_pokemon_name_window_images", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          trainer_id: trainerIdInDB,
          image_labels: nameWindowImageLabels,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        toast({
          title: "Success",
          description: data.message,
        });
      } else {
        const data = await response.json();
        throw new Error(data.detail);
      }
    } catch (error) {
      const typedError = error as any;
      toast({
        title: "Error",
        description: typedError.message,
        variant: "destructive",
      });
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto py-8">
        <div className="flex items-center gap-0">
          <h1 className="text-3xl font-bold p-1">新しいポケモン画像のラベリング</h1>
          <img src="./n426.gif" alt="フワライド" className="w-12 h-12" />
        </div>
        <div className="flex-1 p-4 bg-white rounded-md shadow-sm">
            <div className="flex flex-col items-start space-y-2">
              <p>検出ができなかったポケモン画像一覧</p>
              <p>適切な名前を与えて「Submit」してください。以降の対戦データ抽出で利用されます。</p>
            </div>
        </div>
        <Separator className="my-4" />
        <div className="flex-1 p-4 bg-white rounded-md shadow-sm">
          <h2 className="text-xl font-semibold p-1 mb-4">ポケモン選出画像</h2>
            <div className="grid grid-cols-4 gap-10">
              {imageDataList.imageURLList.map((imageURL, index) => (
              <div key={index} className="flex flex-col items-center space-y-2">
                <img src={imageURL} alt={`Image ${index}`} className="max-w-full h-auto" />
                <Select
                  options={reactSelectOptions}
                  onChange={(option) => handleSelectChange(index, option)}
                />
              </div>
              ))}
            </div>
        </div>
        <Separator className="my-4" />
        <div className="flex-1 p-4 bg-white rounded-md shadow-sm">
            {imageLabels.length === 0 ? <p>ラベルが付与されていないポケモン画像はありません</p> : imageLabels.length === imageDataList.imageURLList.length ?
                <Button onClick={handleSubmit}>Pokemon Image Submit</Button>
                : <p>全てのポケモン画像にラベルを付与してください</p>
            }
        </div>
        <Separator className="my-4" />
        <div className="flex-1 p-4 bg-white rounded-md shadow-sm">
          <h2 className="text-xl font-semibold p-1 mb-4">ポケモンウィンドウ名画像</h2>
          <div className="grid grid-cols-4 gap-10">
              {nameWindowImageDataList.imageURLList.map((imageURL, index) => (
              <div key={index} className="flex flex-col items-center space-y-2">
                <img src={imageURL} alt={`NameWindowImage ${index}`} className="max-w-full h-auto" />
                <Select
                  options={reactSelectOptions}
                  onChange={(option) => handleNameWindowSelectChange(index, option)}
                />
              </div>
              ))}
            </div>
        </div>
        <Separator className="my-4" />
        <div className="flex-1 p-4 bg-white rounded-md shadow-sm">
            {nameWindowImageLabels.length == 0 ? <p>ラベルが付与されていないウィンドウ画像はありません</p> : nameWindowImageLabels.length === nameWindowImageDataList.imageURLList.length ?
                <Button onClick={handleNameWindowSubmit}>Pokemon Name Window Image Submit</Button>
                : <p>全てのウィンドウ画像にラベルを付与してください</p>
            }
        </div>
      </div>
    </div>
  );
};

export default withAuthenticationRequired(AnnotatePokemonImagesPage);
