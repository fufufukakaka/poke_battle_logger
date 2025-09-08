"use client"

import * as React from "react"
import { cn } from "@/lib/utils"

const Timeline = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("relative", className)}
    {...props}
  />
))
Timeline.displayName = "Timeline"

const TimelineItem = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("relative flex gap-4 pb-8 last:pb-0", className)}
    {...props}
  />
))
TimelineItem.displayName = "TimelineItem"

const TimelineMarker = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement> & {
    variant?: "default" | "primary" | "secondary"
  }
>(({ className, variant = "default", ...props }, ref) => (
  <div
    ref={ref}
    className={cn(
      "relative flex shrink-0 items-center justify-center",
      className
    )}
    {...props}
  >
    {/* Vertical line */}
    <div
      className={cn(
        "absolute top-0 h-full w-0.5 -translate-x-1/2",
        variant === "primary" && "bg-blue-500",
        variant === "secondary" && "bg-gray-300",
        variant === "default" && "bg-gray-300"
      )}
    />
    {/* Circle marker */}
    <div
      className={cn(
        "z-10 h-3 w-3 rounded-full border-2 bg-background",
        variant === "primary" && "border-blue-500 bg-blue-500",
        variant === "secondary" && "border-gray-400 bg-gray-400",
        variant === "default" && "border-gray-400 bg-background"
      )}
    />
  </div>
))
TimelineMarker.displayName = "TimelineMarker"

const TimelineContent = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("flex-1 space-y-2", className)}
    {...props}
  />
))
TimelineContent.displayName = "TimelineContent"

const TimelineDate = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn(
      "inline-block rounded px-2 py-1 text-xs font-medium bg-yellow-200 text-yellow-800",
      className
    )}
    {...props}
  />
))
TimelineDate.displayName = "TimelineDate"

const TimelineTitle = React.forwardRef<
  HTMLHeadingElement,
  React.HTMLAttributes<HTMLHeadingElement>
>(({ className, ...props }, ref) => (
  <h3
    ref={ref}
    className={cn("text-lg font-semibold text-blue-600", className)}
    {...props}
  />
))
TimelineTitle.displayName = "TimelineTitle"

const TimelineDescription = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLParagraphElement>
>(({ className, ...props }, ref) => (
  <p
    ref={ref}
    className={cn("text-sm text-muted-foreground", className)}
    {...props}
  />
))
TimelineDescription.displayName = "TimelineDescription"

export {
  Timeline,
  TimelineItem,
  TimelineMarker,
  TimelineContent,
  TimelineDate,
  TimelineTitle,
  TimelineDescription,
}