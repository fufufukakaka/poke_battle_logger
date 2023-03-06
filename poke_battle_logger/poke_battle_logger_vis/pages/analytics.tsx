import { Box, Container } from '@chakra-ui/react';
import { GetServerSideProps } from 'next';
import getWinRateTransitionHandler from './api/get_win_rate_transition';
import WinRateChart from './components/data-display/win-rate-chart';

interface AnalyticsProps {
  win_rates: any;
}

export const getServerSideProps: GetServerSideProps<
  AnalyticsProps
> = async () => {
  const result = await getWinRateTransitionHandler();
  if ('error' in result) {
    throw new Error('error');
  }

  return {
    props: {
      win_rates: result.win_rate,
    },
  };
};

const Analytics: React.FC<AnalyticsProps> = ({ win_rates }) => {
  return (
    <Box bg="gray.50" minH="100vh">
      <Container maxW="container.xl" py="8">
        <Box flex="1" p="4" bg="white">
          <WinRateChart win_rates={win_rates} />
        </Box>
      </Container>
    </Box>
  );
};

export default Analytics;
