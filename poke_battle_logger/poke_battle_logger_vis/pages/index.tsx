import Head from 'next/head'
import Image from 'next/image'
import { Inter } from 'next/font/google'
import styles from '@/styles/Home.module.css'
import {
  Box,
  Flex,
  VStack,
  Heading,
  Link,
  Text,
  Table,
  Thead,
  Tr,
  Th,
  Td,
  Button,
} from '@chakra-ui/react';

import * as React from 'react';

const inter = Inter({ subsets: ['latin'] })
function Frame(props: React.ComponentProps<typeof Box>) {
  return <Box pos="absolute" {...props} />;
}

export default function Home() {
  return (
    <>
      <Head>
        <title>Poke Battle Logger</title>
        <meta name="description" content="ポケモンの対戦動画からデータを抽出して可視化する" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      <Flex width="1280px" height="720px" className="bg-slate-100">
        <Frame top={30} width={222} height={720}>
          <VStack
            alignItems="left"
            height="100%"
            spacing="5px"
            paddingY="10px"
            paddingX="10px"
            backgroundColor="rgba(11,21,48,0.9)"
            backdropFilter="auto"
            backdropBlur="10px"
          >
            <Heading
              color="#fff"
              fontWeight="semibold"
              size="md"
              padding="12px 10px"
            >
              {'Pokemon Battle Logger'}
            </Heading>
            <Link
              padding="8px 10px"
              borderRadius="3px"
              fontSize="12px"
              fontWeight="medium"
              backgroundColor="rgba(255,255,255,0.1)"
              color="#fff"
            >
              {'\u30C0\u30C3\u30B7\u30E5\u30DC\u30FC\u30C9'}
            </Link>
            <Link
              padding="8px 10px"
              borderRadius="3px"
              fontSize="12px"
              fontWeight="normal"
              backgroundColor="transparent"
              color="#fff"
            >
              {'\u5BFE\u6226\u30ED\u30B0'}
            </Link>
            <Link
              padding="8px 10px"
              borderRadius="3px"
              fontSize="12px"
              fontWeight="normal"
              backgroundColor="transparent"
              color="#fff"
            >
              {'\u30ED\u30B0\u5206\u6790'}
            </Link>
            <Link
              padding="8px 10px"
              borderRadius="3px"
              fontSize="12px"
              fontWeight="normal"
              backgroundColor="transparent"
              color="#fff"
            >
              {'\u30C7\u30FC\u30BF\u8FFD\u52A0'}
            </Link>
          </VStack>
        </Frame>
        <Frame left={263} top={30} width={855} height={55}>
          <Flex>
            <Heading flex="1" size="lg" lineHeight="1.3">
              {'\u30C0\u30C3\u30B7\u30E5\u30DC\u30FC\u30C9'}
            </Heading>
          </Flex>
        </Frame>
        <Frame left={263} top={100} width={230} height={181}>
          <Flex
            width="230px"
            height="181px"
            className="bg-white rounded-lg shadow-sm"
          />
        </Frame>
        <Frame left={263} top={301} width={980} height={442}>
          <Flex
            width="980px"
            height="442px"
            className="bg-white rounded-lg shadow-sm"
          />
        </Frame>
        <Frame left={287} top={122} width={38} height={38}>
          <Image
            src="https://api.iconify.design/mdi/crown.svg"
            alt="Picture of the author"
            width={500}
            height={500}
          />
        </Frame>
        <Frame left={287} top={223} width={206} height={32}>
          <Text className="text-blue-600 font-semibold">{'\u9806\u4F4D'}</Text>
        </Frame>
        <Frame left={287} top={162} width={206} height={56}>
          <Flex>
            <Heading flex="1" size="2xl" lineHeight="1.3">
              {'214'}
            </Heading>
          </Flex>
        </Frame>
        <Frame left={513} top={100} width={230} height={181}>
          <Flex
            width="230px"
            height="181px"
            className="bg-white rounded-lg shadow-sm"
          />
        </Frame>
        <Frame left={537} top={122} width={38} height={38}>
          <Image
            src="https://api.iconify.design/material-symbols/punch.svg"
            alt="Picture of the author"
            width={500}
            height={500}
          />
        </Frame>
        <Frame left={537} top={223} width={206} height={32}>
          <Text className="text-green-600 font-semibold">{'\u52DD\u7387'}</Text>
        </Frame>
        <Frame left={537} top={162} width={206} height={56}>
          <Flex>
            <Heading flex="1" size="2xl" lineHeight="1.3">
              {'52.5%'}
            </Heading>
          </Flex>
        </Frame>
        <Frame left={763} top={100} width={230} height={181}>
          <Flex
            width="230px"
            height="181px"
            className="bg-white rounded-lg shadow-sm"
          />
        </Frame>
        <Frame left={787} top={122} width={38} height={38}>
          <Image
            src="https://api.iconify.design/mdi/cancel.svg"
            alt="Picture of the author"
            width={500}
            height={500}
          />
        </Frame>
        <Frame left={787} top={223} width={206} height={32}>
          <Text className="text-orange-600 font-semibold">
            {'\u6700\u8FD1\u8CA0\u3051\u305F\u30DD\u30B1\u30E2\u30F3'}
          </Text>
        </Frame>
        <Frame left={787} top={162} width={206} height={56}>
          <Flex>
            <Heading flex="1" size="lg" lineHeight="1.3">
              {'\u30D8\u30A4\u30E9\u30C3\u30B7\u30E3'}
            </Heading>
          </Flex>
        </Frame>
        <Frame left={1013} top={100} width={230} height={181}>
          <Flex
            width="230px"
            height="181px"
            className="bg-white rounded-lg shadow-sm"
          />
        </Frame>
        <Frame left={1037} top={122} width={38} height={38}>
          <Image
            src="https://api.iconify.design/material-symbols/clock-loader-10.svg"
            alt="Picture of the author"
            width={500}
            height={500}
          />
        </Frame>
        <Frame left={1037} top={223} width={206} height={32}>
          <Text className="text-purple-600 font-semibold">
            {'\u6700\u8FD1\u52DD\u3063\u305F\u30DD\u30B1\u30E2\u30F3'}
          </Text>
        </Frame>
        <Frame left={1037} top={162} width={206} height={56}>
          <Flex>
            <Heading flex="1" size="lg" lineHeight="1.3">
              {'\u30CF\u30D0\u30BF\u30AF\u30AB\u30DF'}
            </Heading>
          </Flex>
        </Frame>
        <Frame left={263} top={360} width={980} height={371}>
          <VStack
            alignItems="left"
            height="100%"
            backgroundColor="rgba(255,255,255,0.9)"
            backdropFilter="auto"
            backdropBlur="10px"
            overflowY="auto"
            border="1px solid #eee"
            color="#000"
          >
            <Table size="md">
              <Thead>
                <Tr>
                  <Th>{'BattleId'}</Th>
                  <Th>{'result'}</Th>
                  <Th>{'\u81EA\u5206\u306E\u521D\u624B'}</Th>
                  <Th>{'\u76F8\u624B\u306E\u521D\u624B'}</Th>
                </Tr>
              </Thead>
              <Tr>
                <Td>{'50086'}</Td>
                <Td>{'WIN'}</Td>
                <Td>{'\u30D5\u30EF\u30E9\u30A4\u30C9'}</Td>
                <Td>{'\u30C9\u30C9\u30B2\u30B6\u30F3'}</Td>
              </Tr>
              <Tr>
                <Td>{'50085'}</Td>
                <Td>{'WIN'}</Td>
                <Td>{'\u30D5\u30EF\u30E9\u30A4\u30C9'}</Td>
                <Td>{'\u30E9\u30A6\u30C9\u30DC\u30FC\u30F3'}</Td>
              </Tr>
              <Tr>
                <Td>{'50084'}</Td>
                <Td>{'WIN'}</Td>
                <Td>{'\u30D8\u30A4\u30E9\u30C3\u30B7\u30E3'}</Td>
                <Td>{'\u30DE\u30B9\u30AB\u30FC\u30CB\u30E3'}</Td>
              </Tr>
              <Tr>
                <Td>{'50083'}</Td>
                <Td>{'WIN'}</Td>
                <Td>{'\u30D5\u30EF\u30E9\u30A4\u30C9'}</Td>
                <Td>{'\u30D5\u30EF\u30E9\u30A4\u30C9'}</Td>
              </Tr>
              <Tr>
                <Td>{'50082'}</Td>
                <Td>{'WIN'}</Td>
                <Td>{'\u30AD\u30CE\u30AC\u30C3\u30B5'}</Td>
                <Td>{'\u30BF\u30AE\u30F3\u30B0\u30EB'}</Td>
              </Tr>
              <Tr>
                <Td>{'50081'}</Td>
                <Td>{'WIN'}</Td>
                <Td>{'\u30CC\u30E1\u30EB\u30B4\u30F3'}</Td>
                <Td>{'\u30CB\u30F3\u30D5\u30A3\u30A2'}</Td>
              </Tr>
            </Table>
          </VStack>
        </Frame>
        <Frame left={287} top={318} width={295} height={35}>
          <Flex>
            <Heading flex="1" size="md" lineHeight="1.3">
              {'\u6700\u8FD1\u306E\u5BFE\u6226\u30ED\u30B0'}
            </Heading>
          </Flex>
        </Frame>
        <Frame left={1037} top={318} width={192} height={35}>
          <Button
            width="192px"
            size="md"
            backgroundColor="#f1f5f9"
            color="#000"
            isDisabled={false}
          >
            {'\u5BFE\u6226\u30ED\u30B0\u8A73\u7D30\u3078'}
          </Button>
        </Frame>
      </Flex>
    </>
  )
}
