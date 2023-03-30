import * as React from 'react';
import {
  Box,
  Center,
  Heading,
  Button,
  VStack,
  useColorModeValue,
} from '@chakra-ui/react';
import NextLink from 'next/link';


export const Login = () => {
  const buttonBgColor = useColorModeValue('blue.600', 'blue.200');
  const buttonHoverBgColor = useColorModeValue('blue.500', 'blue.300');

  return (
    <Box
      height="100vh"
      display="flex"
      flexDirection="column"
      justifyContent="center"
    >
      <Center flexGrow={1}>
        <VStack spacing={8}>
          <Heading fontSize="6xl">PokeBattleLogger</Heading>
          <NextLink href="/api/auth/login" passHref>
            <Button
              size="lg"
              colorScheme="blue"
              backgroundColor={buttonBgColor}
              _hover={{ backgroundColor: buttonHoverBgColor }}
              as="a"
            >
              ログイン
            </Button>
          </NextLink>
        </VStack>
      </Center>
    </Box>
  );
};

export default Login;
