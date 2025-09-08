import React from 'react'
import { IconType } from 'react-icons'
import Link from 'next/link'
import { cn } from '@/lib/utils'

interface NavItemProps {
  icon: IconType
  href: string
  iconSize?: string
  children: React.ReactNode
  className?: string
}

const NavItem = ({ icon: Icon, children, href, iconSize, className }: NavItemProps) => {
  return (
    <Link href={href}>
      <div
        className={cn(
          "flex items-center p-4 mx-4 rounded-lg cursor-pointer hover:bg-cyan-400 hover:text-white text-white break-all group",
          className
        )}
      >
        {Icon && (
          <Icon 
            className="mr-4 group-hover:text-white" 
            size={iconSize ? iconSize : 16}
          />
        )}
        {children}
      </div>
    </Link>
  )
}

export default NavItem
