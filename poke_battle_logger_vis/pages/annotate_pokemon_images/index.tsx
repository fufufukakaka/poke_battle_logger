import { Box, Container, HStack, Heading, Image, Text, Divider, VStack, SimpleGrid, Button } from "@chakra-ui/react";
import React, { useState } from "react";
import { useAuth0, withAuthenticationRequired } from "@auth0/auth0-react";
import useSWR from "swr";
import { getImageUrlClient } from "@/helper/getImageURLClient";
import Select from 'react-select'
import { reactSelectOptions } from "@/helper/pokemonJapaneseToEnglishDict";
import { useToast } from "@chakra-ui/react";


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

  const toast = useToast();

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
          status: "success",
          duration: 3000,
          isClosable: true,
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
        status: "error",
        duration: 3000,
        isClosable: true,
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
          status: "success",
          duration: 3000,
          isClosable: true,
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
        status: "error",
        duration: 3000,
        isClosable: true,
      });
    }
  };

  return (
    <Box bg="gray.50" minH="100vh">
      <Container maxW="container.xl" py="8">
        <HStack spacing={0}>
          <Heading padding={'5px'}>新しいポケモン画像のラベリング</Heading>
          <Image src="./n426.gif" alt="フワライド" boxSize="50px" />
        </HStack>
        <Box flex="1" p="4" bg="white">
            <VStack justify={"start"} align={"start"}>
              <Text>検出ができなかったポケモン画像一覧</Text>
              <Text>適切な名前を与えて「Submit」してください。以降の対戦データ抽出で利用されます。</Text>
            </VStack>
        </Box>
        <Divider />
        <Box flex="1" p="4" bg="white">
          <Heading padding={'5px'} size={'md'}>ポケモン選出画像</Heading>
            <SimpleGrid columns={4} spacing={10}>
              {imageDataList.imageURLList.map((imageURL, index) => (
              <VStack key={index}>
                <Image src={imageURL} alt={`Image ${index}`} />
                <Select
                  options={reactSelectOptions}
                  onChange={(option) => handleSelectChange(index, option)}
                />
              </VStack>
              ))}
            </SimpleGrid>
        </Box>
        <Divider />
        <Box flex="1" p="4" bg="white">
            {imageLabels.length === 0 ? <Text>ラベルが付与されていないポケモン画像はありません</Text> : imageLabels.length === imageDataList.imageURLList.length ?
                <Button colorScheme='blue' onClick={handleSubmit}>Pokemon Image Submit</Button>
                : <Text>全てのポケモン画像にラベルを付与してください</Text>
            }
        </Box>
        <Divider />
        <Box flex="1" p="4" bg="white">
          <Heading padding={'5px'} size={'md'}>ポケモンウィンドウ名画像</Heading>
          <SimpleGrid columns={4} spacing={10}>
              {nameWindowImageDataList.imageURLList.map((imageURL, index) => (
              <VStack key={index}>
                <Image src={imageURL} alt={`NameWindowImage ${index}`} />
                <Select
                  options={reactSelectOptions}
                  onChange={(option) => handleNameWindowSelectChange(index, option)}
                />
              </VStack>
              ))}
            </SimpleGrid>
        </Box>
        <Divider />
        <Box flex="1" p="4" bg="white">
            {nameWindowImageLabels.length == 0 ? <Text>ラベルが付与されていないウィンドウ画像はありません</Text> : nameWindowImageLabels.length === nameWindowImageDataList.imageURLList.length ?
                <Button colorScheme='blue' onClick={handleNameWindowSubmit}>Pokemon Name Window Image Submit</Button>
                : <Text>全てのウィンドウ画像にラベルを付与してください</Text>
            }
        </Box>
      </Container>
    </Box>
  );
};

export default withAuthenticationRequired(AnnotatePokemonImagesPage);
