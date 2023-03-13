import React, {createContext, useState} from 'react'
import type { AppProps } from 'next/app'
import { ChakraProvider } from '@chakra-ui/react'
import Layout from '../components/layouts/layout'

export const SeasonContext = createContext('all')

export default function App({ Component, pageProps }: AppProps) {
  const [season, setSeason] = useState('all');
  return <ChakraProvider>
    <SeasonContext.Provider value={season}>
  <Layout setSeason={setSeason}>
    <Component {...pageProps} />
  </Layout>
  </SeasonContext.Provider>
</ChakraProvider>
}
