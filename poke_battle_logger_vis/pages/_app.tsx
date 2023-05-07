import React, { createContext, useState } from 'react';
import type { AppProps } from 'next/app';
import { ChakraProvider } from '@chakra-ui/react';
import Layout from '../components/layouts/layout';
import Login from '../pages/login/index';
import { Auth0Provider } from '@auth0/auth0-react';
import { Auth0Domain, Auto0ClientId, Auth0CallbackURL } from '../util'

// get season from local storage
let initialSeason = 0
if (typeof window !== "undefined") {
  initialSeason = Number(localStorage.getItem('season'));
}
export const SeasonContext = createContext(initialSeason);

export default function App({ Component, pageProps }: AppProps) {
  const [season, setSeason] = useState(initialSeason);
  const hideSidebar = Component === Login;

  const setSeasonHandler = (season: number) => {
    // set local storage
    localStorage.setItem('season', season.toString());
    // set state
    setSeason(season);
  };

  return (
    <Auth0Provider
      domain={Auth0Domain}
      clientId={Auto0ClientId}
      authorizationParams={{
        redirect_uri: Auth0CallbackURL,
      }}
    >
      <ChakraProvider>
        <SeasonContext.Provider value={season}>
          <Layout season={season} setSeason={setSeasonHandler} hideSidebar={hideSidebar}>
            <Component {...pageProps} />
          </Layout>
        </SeasonContext.Provider>
      </ChakraProvider>
    </Auth0Provider>
  );
}
