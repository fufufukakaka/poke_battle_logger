import React from 'react'
import { Select, Box, CloseButton, Flex, useColorModeValue, Text, BoxProps } from '@chakra-ui/react'
import Link from 'next/link'
import { RiDatabaseFill } from 'react-icons/ri'
import NavItem from '../atoms/NavItem'
import { MdCatchingPokemon } from 'react-icons/md'
import { TbAnalyzeFilled } from 'react-icons/tb'

interface SidebarProps extends BoxProps {
  onClose: () => void
  setSeason: React.Dispatch<React.SetStateAction<string>>
}

const SideBar = ({ onClose, setSeason, ...rest }: SidebarProps) => {
  return (
    <Box
      bg={useColorModeValue('rgba(11, 21, 48, 0.9)', 'gray.900')}
      borderRight="1px"
      borderRightColor={useColorModeValue('gray.200', 'gray.700')}
      w={{ base: 'full', md: 60 }}
      pos="fixed"
      h="full"
      {...rest}
    >
      <Flex h="20" alignItems="center" mx="8" justifyContent="space-between" marginY="20px">
        <Text fontSize="2xl" fontFamily="monospace" fontWeight="bold" color="white">
          <Link href="/">Poke Battle Logger</Link>
        </Text>
        <CloseButton display={{ base: 'flex', md: 'none' }} onClick={onClose} />
      </Flex>
      <Select defaultValue='all' color='white' onChange={(e) => setSeason(e.target.value)}>
        <option value={0}>全シーズン</option>
        <option value={3}>シーズン3</option>
        <option value={4}>シーズン4</option>
      </Select>
      <NavItem key={'dashboard'} icon={MdCatchingPokemon} href={'/'} marginBottom="5px">
        ダッシュボード
      </NavItem>
      <NavItem key={'analytics'} icon={TbAnalyzeFilled} href={'/analytics'} marginTop="5px">
        ログ分析
      </NavItem>
      <NavItem key={'all_log'} icon={RiDatabaseFill} href={'/all_battle_log'} marginTop="5px">
        対戦ログ一覧
      </NavItem>
    </Box>
  )
}

export default SideBar
