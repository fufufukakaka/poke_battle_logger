import type { AppProps } from 'next/app'
import { ChakraProvider } from '@chakra-ui/react'
import Layout from './components/layouts/layout'

export default function App({ Component, pageProps }: AppProps) {
  return <ChakraProvider>
  <Layout>
    <Component {...pageProps} />
  </Layout>
</ChakraProvider>
}
