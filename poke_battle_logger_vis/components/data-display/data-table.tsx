import * as React from 'react';
import {
  HStack,
  Table,
  Thead,
  Tbody,
  Tr,
  Th,
  Td,
  chakra,
  Input,
  VStack,
} from '@chakra-ui/react';
import { TriangleDownIcon, TriangleUpIcon } from '@chakra-ui/icons';
import {
  useReactTable,
  flexRender,
  getCoreRowModel,
  ColumnDef,
  SortingState,
  getSortedRowModel,
} from '@tanstack/react-table';
import PokemonIcon from '../atoms/pokemon-icon';

type PokemonStat = {
  pokemon_name: string;
  in_team_rate: number;
  in_battle_rate: number;
  head_battle_rate: number;
  in_battle_win_rate: number;
  in_battle_lose_rate: number;
}

export type DataTableProps<Data extends object & PokemonStat> = {
  data: Data[];
  columns: ColumnDef<Data, any>[];
};

export function DataTable<Data extends object & PokemonStat>({
  data,
  columns,
}: DataTableProps<Data>) {
  const [sorting, setSorting] = React.useState<SortingState>([]);
  const [searchText, setSearchText] = React.useState('');

  const filteredData = React.useMemo(() => {
    const filterData = (data: Data[], searchText: string): Data[] => {
      if (!searchText) return data;

      return data.filter((row) => {
        if (row.hasOwnProperty('pokemon_name')) {
          const pokemonName = row['pokemon_name'] as string;
          return pokemonName.toLowerCase().startsWith(searchText.toLowerCase());
        }
        return false;
      });
    }
    return filterData(data, searchText);
  }, [data, searchText]);

  const table = useReactTable({
    columns,
    data: filteredData,
    getCoreRowModel: getCoreRowModel(),
    onSortingChange: setSorting,
    getSortedRowModel: getSortedRowModel(),
    state: {
      sorting,
    },
  });

  return (
    <VStack>
      <Input
        placeholder="ポケモン名を入力して検索"
        value={searchText}
        onChange={(e) => setSearchText(e.target.value)}
      />
      <Table>
      <Thead>
        {table.getHeaderGroups().map((headerGroup) => (
          <Tr key={headerGroup.id}>
            {headerGroup.headers.map((header) => {
              // see https://tanstack.com/table/v8/docs/api/core/column-def#meta to type this correctly
              const meta: any = header.column.columnDef.meta;
              return (
                <Th
                  key={header.id}
                  onClick={header.column.getToggleSortingHandler()}
                  isNumeric={meta?.isNumeric}
                >
                  {flexRender(
                    header.column.columnDef.header,
                    header.getContext()
                  )}

                  <chakra.span pl="4">
                    {header.column.getIsSorted() ? (
                      header.column.getIsSorted() === 'desc' ? (
                        <TriangleDownIcon aria-label="sorted descending" />
                      ) : (
                        <TriangleUpIcon aria-label="sorted ascending" />
                      )
                    ) : null}
                  </chakra.span>
                </Th>
              );
            })}
          </Tr>
        ))}
      </Thead>
      <Tbody>
        {table.getRowModel().rows.map((row) => (
          <Tr key={row.id}>
            {row.getVisibleCells().map((cell) => {
              // see https://tanstack.com/table/v8/docs/api/core/column-def#meta to type this correctly
              const meta: any = cell.column.columnDef.meta;
              // slice column name ex. 74_pokemon_name
              const columnName =
                cell.id.split('_')[1] + '_' + cell.id.split('_')[2];
              return (
                <Td key={cell.id} isNumeric={meta?.isNumeric}>
                  {columnName === 'pokemon_name' ? (
                    <HStack spacing={0} align="center">
                      {flexRender(cell.column.columnDef.cell, cell.getContext())}
                      <div>
                        <PokemonIcon
                          key={cell.getValue() as string}
                          pokemon_name={cell.getValue() as string}
                          boxSize={'60px'}
                        />
                      </div>
                    </HStack>
                  ) : (
                    flexRender(cell.column.columnDef.cell, cell.getContext())
                  )}
                </Td>
              );
            })}
          </Tr>
        ))}
      </Tbody>
    </Table>
    </VStack>
  );
}
