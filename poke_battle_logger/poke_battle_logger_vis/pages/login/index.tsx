import * as React from 'react';
import {
  Box,
  Center,
  Heading,
  Button,
  VStack,
  useColorModeValue,
} from '@chakra-ui/react';
import { useAuth0 } from "@auth0/auth0-react";

export interface PageProps {
    hideSidebar?: boolean;
  }

export const Login = (pageProps: PageProps) => {
  const buttonBgColor = useColorModeValue('blue.600', 'blue.200');
  const buttonHoverBgColor = useColorModeValue('blue.500', 'blue.300');
  const { isAuthenticated, loginWithRedirect } = useAuth0();

  return (
    <Box height="100vh" display="flex" flexDirection="column" justifyContent="center">
      <Center flexGrow={1}>
        <VStack spacing={8}>
          <Heading fontSize="6xl">PokeBattleLogger</Heading>
          <Button
            size="lg"
            colorScheme="blue"
            backgroundColor={buttonBgColor}
            _hover={{ backgroundColor: buttonHoverBgColor }}
            onClick={() => loginWithRedirect()}
          >
            ログイン
          </Button>
        </VStack>
      </Center>
    </Box>
  );
};

Login.hideSidebar = true;
export default Login;
