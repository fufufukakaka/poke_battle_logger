import React from 'react';
import { Button } from '@/components/ui/button';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { cn } from '@/lib/utils';

interface PaginationControllerProps {
    maxPage: number;
    currentPage: number;
    setCurrentPage: (page: number) => void;
}

const PaginationController: React.FC<PaginationControllerProps> = ({
    maxPage,
    currentPage,
    setCurrentPage,
}) => {
  const nextPage = () => {
    if (currentPage < maxPage) {
      setCurrentPage(currentPage + 1);
    }
  };

  const prevPage = () => {
    if (currentPage > 1) {
      setCurrentPage(currentPage - 1);
    }
  };

  const renderPageNumbers = () => {
    const pageNumbers = [];
    const startPage = Math.max(1, currentPage - 2);
    const endPage = Math.min(maxPage, currentPage + 2);

    for (let i = startPage; i <= endPage; i++) {
      pageNumbers.push(
        <Button
          key={i}
          onClick={() => setCurrentPage(i)}
          variant={i === currentPage ? 'default' : 'outline'}
          className={cn(
            "h-9 w-9 p-0",
            i === currentPage && "pointer-events-none"
          )}
        >
          {i}
        </Button>,
      );
    }

    if (startPage > 1) {
      pageNumbers.unshift(
        <span key="start-ellipsis" className="mx-2 text-gray-500">
          ...
        </span>,
      );
    }
    if (endPage < maxPage) {
      pageNumbers.push(
        <span key="end-ellipsis" className="mx-2 text-gray-500">
          ...
        </span>,
      );
    }

    return pageNumbers;
  };

  return (
    <div className="flex justify-center items-center bg-white rounded-md shadow-sm p-4">
      <div className="flex items-center gap-2">
        <Button
          onClick={prevPage}
          disabled={currentPage === 1}
          variant="outline"
          size="icon"
          className="h-9 w-9"
        >
          <ChevronLeft className="h-4 w-4" />
        </Button>
        {renderPageNumbers()}
        <Button
          onClick={nextPage}
          disabled={currentPage === maxPage}
          variant="outline"
          size="icon"
          className="h-9 w-9"
        >
          <ChevronRight className="h-4 w-4" />
        </Button>
      </div>
    </div>
  );
};

export default PaginationController;
