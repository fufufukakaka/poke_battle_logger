import * as React from 'react';
import { ChevronDown, ChevronUp } from 'lucide-react';
import {
  useReactTable,
  flexRender,
  getCoreRowModel,
  ColumnDef,
  SortingState,
  getSortedRowModel,
} from '@tanstack/react-table';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Input } from '@/components/ui/input';
import PokemonIcon from '../atoms/pokemon-icon';

type PokemonStat = {
  your_pokemon_name: string;
  opponent_pokemon_name: string;
  knock_out_count: number;
}

export type DataTableProps<Data extends object & PokemonStat> = {
  data: Data[];
  columns: ColumnDef<Data, any>[];
};

export function PokemonKnockOutDataTable<Data extends object & PokemonStat>({
  data,
  columns,
}: DataTableProps<Data>) {
  const [sorting, setSorting] = React.useState<SortingState>([]);
  const [searchText, setSearchText] = React.useState('');

  const filteredData = React.useMemo(() => {
    const filterData = (data: Data[], searchText: string): Data[] => {
      if (!searchText) return data;

      return data.filter((row) => {
        if (row.hasOwnProperty('your_pokemon_name')) {
          const pokemonName = row['your_pokemon_name'] as string;
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
    <div className="space-y-4">
      <Input
        placeholder="自分のポケモン名を入力して検索"
        value={searchText}
        onChange={(e) => setSearchText(e.target.value)}
        className="max-w-sm"
      />
      <div className="rounded-md border">
        <Table>
          <TableHeader>
            {table.getHeaderGroups().map((headerGroup) => (
              <TableRow key={headerGroup.id}>
                {headerGroup.headers.map((header) => {
                  const meta: any = header.column.columnDef.meta;
                  return (
                    <TableHead
                      key={header.id}
                      className={`cursor-pointer select-none ${meta?.isNumeric ? 'text-right' : ''}`}
                      onClick={header.column.getToggleSortingHandler()}
                    >
                      <div className="flex items-center gap-2">
                        {flexRender(
                          header.column.columnDef.header,
                          header.getContext()
                        )}
                        <span className="ml-2">
                          {header.column.getIsSorted() ? (
                            header.column.getIsSorted() === 'desc' ? (
                              <ChevronDown className="h-4 w-4" />
                            ) : (
                              <ChevronUp className="h-4 w-4" />
                            )
                          ) : null}
                        </span>
                      </div>
                    </TableHead>
                  );
                })}
              </TableRow>
            ))}
          </TableHeader>
          <TableBody>
            {table.getRowModel().rows.map((row) => (
              <TableRow key={row.id}>
                {row.getVisibleCells().map((cell) => {
                  const meta: any = cell.column.columnDef.meta;
                  const columnName =
                    cell.id.split('_')[1] + '_' + cell.id.split('_')[2] + '_' + cell.id.split('_')[3];
                  return (
                    <TableCell key={cell.id} className={meta?.isNumeric ? 'text-right' : ''}>
                      {columnName === 'your_pokemon_name' || columnName === 'opponent_pokemon_name' ? (
                        <div className="flex items-center gap-2">
                          {flexRender(cell.column.columnDef.cell, cell.getContext())}
                          <PokemonIcon
                            key={cell.getValue() as string}
                            pokemon_name={cell.getValue() as string}
                            boxSize={'60px'}
                          />
                        </div>
                      ) : (
                        flexRender(cell.column.columnDef.cell, cell.getContext())
                      )}
                    </TableCell>
                  );
                })}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}