import React, { createContext, useState } from 'react';
import type { AppProps } from 'next/app';
import Layout from '../components/layouts/layout';
import Login from '../pages/login/index';
import { Auth0Provider } from '@auth0/auth0-react';
import { Auth0Domain, Auto0ClientId, Auth0CallbackURL } from '../util'
import useSWR from 'swr';
import '../styles/globals.css';
import { Toaster } from '@/components/ui/toaster';

// get season from local storage
let initialSeason = 0
if (typeof window !== "undefined") {
  initialSeason = Number(localStorage.getItem('season'));
}
export const SeasonContext = createContext(initialSeason);

const fetcher = async (url: string) => {
  const res = await fetch(url);
  const data = await res.json();
  return data
}

export default function App({ Component, pageProps }: AppProps) {
  const { data: seasonList } = useSWR("/api/get_seasons", fetcher);

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
      <SeasonContext.Provider value={season}>
        <Layout seasonList={seasonList} season={season} setSeason={setSeasonHandler} hideSidebar={hideSidebar}>
          <Component {...pageProps} />
        </Layout>
        <Toaster />
      </SeasonContext.Provider>
    </Auth0Provider>
  );
}
