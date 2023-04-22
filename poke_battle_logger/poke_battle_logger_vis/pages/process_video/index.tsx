import { Alert, AlertIcon, Spinner, Badge, Box, Button, Container, Progress, Stack, HStack, Heading, Image, Text, InputGroup, InputLeftAddon, Input, Divider, VStack, Radio, RadioGroup } from "@chakra-ui/react";
import React, { useState } from "react";
import axios from 'axios';
import { useAuth0 } from "@auth0/auth0-react";

interface videoFormat {
    isValid: boolean;
    is1080p: boolean;
    is30fps: boolean;
}

const ProcessVideoPage = () => {
  const [progress, setProgress] = useState(0);
  const [jobStatusList, setJobStatusList] = useState<string[]>(["INFO: idle"]);
  const [videoId, setVideoId] = useState("");
  const [videoFormat, setVideoFormat] = useState<videoFormat | undefined>(undefined);
  const [langInVideo, setLangInVideo] = useState('en')
  const [showSpinner, setShowSpinner] = useState(false)
  const { user } = useAuth0();

  const handleOnChange = (value: string) => {
    setVideoId(value);
  };

  const handleOnClick = async () => {
    const checkResult: {"data": videoFormat} = await axios.get("api/check_video_format?videoId=" + videoId);
    setVideoFormat(checkResult.data)
  };

  const handleExtractJob = async () => {
    setShowSpinner(true)
    const socket = new WebSocket(`ws://127.0.0.1:8000/api/v1/extract_stats_from_video?videoId=${videoId}&language=${langInVideo}&trainerId=${user?.sub?.replace("|", "_")}`);
    socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        setProgress(data.progress);
        setJobStatusList(data.message)
    }
    socket.onclose = () => {
      setShowSpinner(false);
    };
  }

  return (
    <Box bg="gray.50" minH="100vh">
      <Container maxW="container.xl" py="8">
        <HStack spacing={0}>
          <Heading padding={'5px'}>対戦データ登録</Heading>
          <Image src="./n426.gif" alt="フワライド" boxSize="50px" />
        </HStack>
        <Box flex="1" p="4" bg="white">
            <VStack justify={"start"} align={"start"}>
            <Text>Youtube の動画(1080p: 30fps) のID を入力してください</Text>
            <InputGroup size='sm'>
                <InputLeftAddon children={'https://www.youtube.com/watch?v='} />
                <Input placeholder='videoId' value={videoId} onChange={(e) => handleOnChange(e.target.value)}/>
            </InputGroup>
            <Button colorScheme='blue' onClick={() => handleOnClick()}>Check Format</Button>
            </VStack>
        </Box>
        <Divider />
        <Box flex="1" p="4" bg="white">
            {videoFormat && (
                <Text>動画のフォーマット: {videoFormat.isValid ? <Badge colorScheme='green'>OK</Badge> : <Badge colorScheme='red'>NO</Badge>} </Text>
            )}
            {videoFormat && !videoFormat.isValid && (
                <Text>動画が 1080p かどうか: {videoFormat.is1080p ? <Badge colorScheme='green'>OK</Badge> : <Badge colorScheme='red'>NO</Badge>}</Text>
            )}
            {videoFormat && !videoFormat.isValid && (
                <Text>動画が 30fps かどうか: {videoFormat.is30fps ? <Badge colorScheme='green'>OK</Badge> : <Badge colorScheme='red'>NO</Badge>}</Text>
            )}
        </Box>
        {videoFormat && videoFormat.isValid ? (
          <>
          <Divider />
            <Box flex="1" p="4" bg="white">
                    <RadioGroup onChange={setLangInVideo} value={langInVideo} marginBottom={"10px"}>
                        <Stack direction='row'>
                            <Radio value='en'>English</Radio>
                            <Radio value='ja'>Japanese</Radio>
                        </Stack>
                    </RadioGroup>
                    <Button colorScheme='green' onClick={() => handleExtractJob()} marginBottom={"10px"}>Start Process Video</Button>
                    {showSpinner && <Spinner marginLeft={"10px"} />}
                    <Progress size='xs' value={progress} />
                    {
                        jobStatusList.map((status, index) => {
                            return (
                                <Stack direction='row'>
                                    {/* もし status が INFO から始まるなら success, ERROR から始まるなら error にする */}
                                    {/* <Alert key={index} status='success' variant='subtle' marginTop={"10px"}>
                                        <AlertIcon />
                                        {status}
                                    </Alert> */}
                                    <Alert key={index} status={status.startsWith('INFO') ? 'success' : 'error'} variant='subtle' marginTop={"10px"}>
                                        <AlertIcon />
                                        {status}
                                    </Alert>
                                </Stack>
                            )
                        })
                    }
            </Box>
          </>
        ) : null}
      </Container>
    </Box>
  );
};

export default ProcessVideoPage;
