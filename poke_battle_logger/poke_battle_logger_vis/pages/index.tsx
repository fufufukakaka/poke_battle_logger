import {
  Box,
  Heading,
  Container,
  Stack,
  Table,
  Tbody,
  Td,
  Th,
  Thead,
  Tr,
  Flex,
  Stat,
  StatLabel,
  StatNumber,
  StatGroup,
  StatHelpText,
  StatArrow,
  useColorModeValue,
} from '@chakra-ui/react';

const menuItems = [
  { label: 'Menu Item 1' },
  { label: 'Menu Item 2' },
  { label: 'Menu Item 3' },
];

const Dashboard = () => {
  return (
    <Box bg="gray.50" minH="100vh">
      <Container maxW="container.xl" py="8">
          <Box flex="1" p="4" bg="white">
            <Stack spacing={4}>
              <StatGroup>
              <Stat
      px={{ base: 4, md: 8 }}
      py={'5'}
      shadow={'s'}
      rounded={'lg'}>
                  <StatLabel fontWeight={'medium'}>勝率 👊</StatLabel>
                  <StatNumber>54%</StatNumber>
                  <StatHelpText>
                    <StatArrow type="increase" />
                    2%
                  </StatHelpText>
                </Stat>
                <Stat
      px={{ base: 4, md: 8 }}
      py={'5'}
      shadow={'s'}
      rounded={'lg'}>
                  <StatLabel fontWeight={'medium'}>順位 👑</StatLabel>
                  <StatNumber>80900</StatNumber>
                  <StatHelpText>
                    <StatArrow type="decrease" />
                    10000
                  </StatHelpText>
                </Stat>
                <Stat
      px={{ base: 4, md: 8 }}
      py={'5'}
      shadow={'s'}
      rounded={'lg'}>
                  <StatLabel fontWeight={'medium'}>最近勝ったポケモン ⭕</StatLabel>
                  <StatNumber>ヘイラッシャ</StatNumber>
                </Stat>
                <Stat
      px={{ base: 4, md: 8 }}
      py={'5'}
      shadow={'s'}
      rounded={'lg'}>
                  <StatLabel fontWeight={'medium'}>最近負けたポケモン ❎</StatLabel>
                  <StatNumber>ハバタクカミ</StatNumber>
                </Stat>
              </StatGroup>
              <Table>
                <Thead>
                  <Tr>
                    <Th>Name</Th>
                    <Th>Email</Th>
                    <Th>Phone</Th>
                  </Tr>
                </Thead>
                <Tbody>
                  <Tr>
                    <Td>John Doe</Td>
                    <Td>john@example.com</Td>
                    <Td>555-555-5555</Td>
                  </Tr>
                  <Tr>
                    <Td>Jane Doe</Td>
                    <Td>jane@example.com</Td>
                    <Td>555-555-5555</Td>
                  </Tr>
                </Tbody>
              </Table>
            </Stack>
          </Box>
      </Container>
    </Box>
  );
};

export default Dashboard;
