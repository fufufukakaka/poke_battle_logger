import { Inter } from 'next/font/google'

import {
  Box,
  VStack,
  Heading,
  Link,
} from '@chakra-ui/react';

import * as React from 'react';

const inter = Inter({ subsets: ['latin'] })
function Frame(props: React.ComponentProps<typeof Box>) {
  return <Box pos="absolute" {...props} />;
}

export default function Sidebar() {
  return (
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
  )
}
