// pages/index.tsx
import { Box, Container, HStack, Heading, Image, Text, Divider, VStack } from "@chakra-ui/react";
import React from "react";
import { useAuth0, withAuthenticationRequired } from "@auth0/auth0-react";
import useSWR from "swr";
import { getImageUrlClient } from "@/helper/getImageURLClient";


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
    const imageList = data.imageList as string[];

    const imageURLList = await Promise.all(
      imageList.map(async (fileName) => {
        const url = await getImageUrlClient(fileName);
        return url;
      })
    );

    return imageURLList;
  }

const AnnotatePokemonImagesPage = () => {
  const { user } = useAuth0();
  const trainerId = user?.sub?.replace("|", "_");
  const { data: dataTrainerIdInDB } = useSWR(`/api/get_trainer_id_in_DB?trainerId=${trainerId}`, fetcher);
  const trainerIdInDB = dataTrainerIdInDB;

  const { data, error } = useSWR(trainerIdInDB ? `/api/unknown_pokemon_images?trainer_id=${trainerIdInDB}` : null, URLfetcher);
  const imageURLList = data || [];

  if (error) return <div>Error loading images</div>;
  if (!data) return <div>Loading...</div>;

  return (
    <Box bg="gray.50" minH="100vh">
      <Container maxW="container.xl" py="8">
        <HStack spacing={0}>
          <Heading padding={'5px'}>新しいポケモン画像のラベリング</Heading>
          <Image src="./n426.gif" alt="フワライド" boxSize="50px" />
        </HStack>
        <Box flex="1" p="4" bg="white">
            <VStack justify={"start"} align={"start"}>
              <Text>ここにたくさん画像が並びます</Text>
            </VStack>
        </Box>
        <Divider />
        <Box flex="1" p="4" bg="white">
            <VStack justify={"start"} align={"start"}>
            {imageURLList.map((imageURL, index) => (
              <Image key={index} src={imageURL} alt={`Image ${index}`} />
            ))}
            </VStack>
        </Box>
      </Container>
    </Box>
  );
};

export default withAuthenticationRequired(AnnotatePokemonImagesPage);
