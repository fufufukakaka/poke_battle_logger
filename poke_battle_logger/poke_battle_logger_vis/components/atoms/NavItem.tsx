import React from 'react'
import { Flex, Icon, FlexProps } from '@chakra-ui/react'
import { IconType } from 'react-icons'
import { ReactText } from 'react'
import Link from 'next/link'

interface NavItemProps extends FlexProps {
  icon: IconType
  href: string
  iconSize?: string
  children: ReactText
}

const NavItem = ({ icon, children, href, iconSize, ...rest }: NavItemProps) => {
  return (
    <Link href={href}>
      <Flex
        align="center"
        p="4"
        mx="4"
        borderRadius="lg"
        role="group"
        cursor="pointer"
        _hover={{
          bg: 'cyan.400',
          color: 'white'
        }}
        color="white"
        overflowWrap="anywhere"
        {...rest}
      >
        {icon && (
          <Icon
            mr="4"
            fontSize={iconSize ? iconSize : '16'}
            _groupHover={{
              color: 'white'
            }}
            as={icon}
          />
        )}
        {children}
      </Flex>
    </Link>
  )
}

export default NavItem
