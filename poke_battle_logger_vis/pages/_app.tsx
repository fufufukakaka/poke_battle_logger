import React, { createContext, useState } from 'react';
import type { AppProps } from 'next/app';
import { ChakraProvider } from '@chakra-ui/react';
import Layout from '../components/layouts/layout';
import Login from '../pages/login/index';
import { Auth0Provider } from '@auth0/auth0-react';
import { Auth0Domain, Auto0ClientId, ServerHost } from './util'

export const SeasonContext = createContext(0);

export default function App({ Component, pageProps }: AppProps) {
  const [season, setSeason] = useState(0);
  const hideSidebar = Component === Login;

  return (
    <Auth0Provider
      domain={Auth0Domain}
      clientId={Auto0ClientId}
      authorizationParams={{
        redirect_uri: ServerHost,
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
