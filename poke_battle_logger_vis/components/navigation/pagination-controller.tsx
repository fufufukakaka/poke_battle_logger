import React, { useState } from 'react';
import {
  Box,
  Button,
  ButtonGroup,
  IconButton,
  Text,
  Spacer,
} from '@chakra-ui/react';
import { ChevronLeftIcon, ChevronRightIcon } from '@chakra-ui/icons';

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
          variant={i === currentPage ? 'solid' : 'outline'}
          colorScheme="blackAlpha"
        >
          {i}
        </Button>,
      );
    }

    if (startPage > 1) {
      pageNumbers.unshift(
        <Text key="start-ellipsis" mx={2} color="black">
          ...
        </Text>,
      );
    }
    if (endPage < maxPage) {
      pageNumbers.push(
        <Text key="end-ellipsis" mx={2} color="black">
          ...
        </Text>,
      );
    }

    return pageNumbers;
  };

  return (
    <Box
      display="flex"
      justifyContent="center"
      alignItems="center"
      backgroundColor="white"
      borderRadius="md"
      boxShadow="sm"
      p={4}
    >
      <ButtonGroup spacing={4}>
        <IconButton
          onClick={prevPage}
          disabled={currentPage === 1}
          icon={<ChevronLeftIcon />}
          aria-label="Previous"
          color="black"
        />
        {renderPageNumbers()}
        <IconButton
          onClick={nextPage}
          disabled={currentPage === maxPage}
          icon={<ChevronRightIcon />}
          aria-label="Next"
          color="black"
        />
      </ButtonGroup>
    </Box>
  );
};

export default PaginationController;
