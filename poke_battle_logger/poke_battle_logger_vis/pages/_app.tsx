import React, { createContext, useState } from 'react';
import type { AppProps } from 'next/app';
import { ChakraProvider } from '@chakra-ui/react';
import Layout from '../components/layouts/layout';
import { UserProvider } from '@auth0/nextjs-auth0/client'
import Login from '../pages/login/index';

export const SeasonContext = createContext(0);

export default function App({ Component, pageProps }: AppProps) {
  const [season, setSeason] = useState(0);

  return (
    <UserProvider>
      <ChakraProvider>
        <SeasonContext.Provider value={season}>
          <Layout setSeason={setSeason}>
            <Component {...pageProps} />
          </Layout>
        </SeasonContext.Provider>
      </ChakraProvider>
    </UserProvider>
  );
}
