import { Alert, AlertIcon, Spinner, Badge, Box, Button, Container, Progress, Stack, HStack, Heading, Image, Text, InputGroup, InputLeftAddon, Input, Divider, VStack, Radio, RadioGroup } from "@chakra-ui/react";
import React, { useState } from "react";
import axios from 'axios';
import { useAuth0, withAuthenticationRequired } from "@auth0/auth0-react";
import { ServerHost, ServerHostWebsocket } from "../../util"
import useSWR from "swr";
import {
  Table,
  Thead,
  Tbody,
  Tfoot,
  Tr,
  Th,
  Td,
  TableCaption,
  TableContainer,
} from '@chakra-ui/react'

interface videoFormat {
    isValid: boolean;
    is1080p: boolean;
    is30fps: boolean;
}

const fetcher = async (url: string) => {
  const res = await fetch(url);
  const data = await res.json();
  return data
}

const ProcessVideoPage = () => {
  const [progress, setProgress] = useState(0);
  const [jobStatusList, setJobStatusList] = useState<string[]>(["INFO: idle"]);
  const [videoId, setVideoId] = useState("");
  const [videoFormat, setVideoFormat] = useState<videoFormat | undefined>(undefined);
  const [langInVideo, setLangInVideo] = useState('en')
  const [showSpinner, setShowSpinner] = useState(false)
  const { user } = useAuth0();
  const trainerId = user?.sub?.replace("|", "_");
  const { data: dataVideoStatus } = useSWR(`/api/get_video_process_status?trainerId=${trainerId}`, fetcher);

  const handleOnChange = (value: string) => {
    setVideoId(value);
  };

  const handleOnClick = async () => {
    const checkResult: {"data": videoFormat} = await axios.get(`${ServerHost}/api/v1/check_video_format?videoId=${videoId}`);
    setVideoFormat(checkResult.data)
  };

  const handleExtractJob = async () => {
    setShowSpinner(true)
    const socket = new WebSocket(`${ServerHost}/api/v1/extract_stats_from_video?videoId=${videoId}&language=${langInVideo}&trainerId=${user?.sub?.replace("|", "_")}`);
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
                <InputLeftAddon>{'https://www.youtube.com/watch?v='}</InputLeftAddon>
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
                                <Stack key={index} direction='row'>
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
        {dataVideoStatus && dataVideoStatus.length > 0 ? <TableContainer>
          <Table variant='simple'>
            <Thead>
              <Tr>
                <Th>動画ID</Th>
                <Th>登録日</Th>
                <Th>処理状況</Th>
              </Tr>
            </Thead>
            <Tbody>
              <Tr>
                <Td>inches</Td>
                <Td>millimetres (mm)</Td>
                <Td isNumeric>25.4</Td>
              </Tr>
            </Tbody>
          </Table>
        </TableContainer> : <p>まだ登録された動画がありません。動画を登録して対戦情報を抽出してみましょう。</p>}
      </Container>
    </Box>
  );
};

export default withAuthenticationRequired(ProcessVideoPage);
