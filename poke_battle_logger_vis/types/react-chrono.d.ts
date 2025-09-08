declare module 'react-chrono' {
  import { ReactNode } from 'react';

  export interface TimelineItem {
    title?: string;
    cardTitle?: string;
    cardSubtitle?: string;
    cardDetailedText?: string | ReactNode;
    media?: {
      source?: {
        url?: string;
      };
      type?: 'IMAGE' | 'VIDEO';
    };
  }

  export interface ChronoProps {
    items?: TimelineItem[];
    mode?: 'HORIZONTAL' | 'VERTICAL' | 'VERTICAL_ALTERNATING';
    theme?: {
      primary?: string;
      secondary?: string;
      cardBgColor?: string;
      cardForeColor?: string;
      titleColor?: string;
      titleColorActive?: string;
    };
    cardHeight?: number;
    disableNavOnKey?: boolean;
    slideShow?: boolean;
    slideItemDuration?: number;
    itemWidth?: number;
    scrollable?: {
      scrollbar?: boolean;
    };
    enableOutline?: boolean;
    allowDynamicUpdate?: boolean;
    useReadMore?: boolean;
    children?: ReactNode;
    className?: string;
  }

  export const Chrono: React.FC<ChronoProps>;
}