import React from 'react'
import { FiMenu } from 'react-icons/fi'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'

interface MobileProps {
  onOpen: () => void
  className?: string
}

const MobileNav = ({ onOpen, className }: MobileProps) => {
  return (
    <div
      className={cn(
        "md:ml-60 px-4 md:px-24 h-20 flex items-center bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700 justify-start",
        className
      )}
    >
      <Button 
        variant="outline" 
        size="icon"
        onClick={onOpen} 
        aria-label="open menu"
      >
        <FiMenu className="h-4 w-4" />
      </Button>

      <span className="text-2xl ml-8 font-mono font-bold">
        Poke Battle Logger
      </span>
    </div>
  )
}

export default MobileNav
