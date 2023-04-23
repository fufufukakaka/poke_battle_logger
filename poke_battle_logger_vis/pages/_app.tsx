import React, { createContext, useState } from 'react';
import type { AppProps } from 'next/app';
import { ChakraProvider } from '@chakra-ui/react';
import Layout from '../components/layouts/layout';
import Login from '../pages/login/index';
import { Auth0Provider } from '@auth0/auth0-react';

export const SeasonContext = createContext(0);

export default function App({ Component, pageProps }: AppProps) {
  const [season, setSeason] = useState(0);
  const hideSidebar = Component === Login;

  return (
    <Auth0Provider
      domain={process.env.NEXT_PUBLIC_AUTH0_DOMAIN}
      clientId={process.env.NEXT_PUBLIC_AUTH0_CLIENT_ID}
      authorizationParams={{
        redirect_uri: "http://localhost:3000",
      }}
    >
      <ChakraProvider>
        <SeasonContext.Provider value={season}>
          <Layout setSeason={setSeason} hideSidebar={hideSidebar}>
            <Component {...pageProps} />
          </Layout>
        </SeasonContext.Provider>
      </ChakraProvider>
    </Auth0Provider>
  );
}