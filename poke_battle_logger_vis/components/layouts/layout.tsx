import React, { DispatchWithoutAction, ReactNode } from 'react';
import {
  Box,
  useColorModeValue,
  Drawer,
  DrawerContent,
  useDisclosure,
} from '@chakra-ui/react';
import SideBar from './sidebar';
import MobileNav from '../atoms/MobileNav';

export default function Layout({
  season,
  setSeason,
  hideSidebar,
  children,
}: {
  season: number;
  setSeason: (season: number) => void;
  hideSidebar: boolean;
  children: ReactNode;
}) {
  const { isOpen, onOpen, onClose } = useDisclosure();
  return (
    <Box minH="100vh" bg={useColorModeValue('gray.100', 'gray.900')}>
      {hideSidebar ? (
        <Box p="4">
          {children}
        </Box>
      ) : (
        <>
          <SideBar
            onClose={() => onClose}
            display={{ base: 'none', md: 'block' }}
            setSeason={setSeason}
            season={season}
          />
          <Drawer
            autoFocus={false}
            isOpen={isOpen}
            placement="left"
            onClose={onClose}
            returnFocusOnClose={false}
            onOverlayClick={onClose}
            size="full"
          >
            <DrawerContent>
              <SideBar season={season} onClose={onClose} setSeason={setSeason} />
            </DrawerContent>
          </Drawer>
          <MobileNav display={{ base: 'flex', md: 'none' }} onOpen={onOpen} />
          <Box ml={{ base: 0, md: 60 }} p="4">
            {children}
          </Box>
        </>
      )}
    </Box>
  );
}
