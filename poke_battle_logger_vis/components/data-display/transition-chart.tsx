"use client"

import { LineChart, Line, CartesianGrid, XAxis, YAxis, ResponsiveContainer, Tooltip } from 'recharts';

interface TransitionChartProps {
  data: number[];
  chartTitle?: string;
  dataLabel?: string;
  dataColor?: string;
  dataBackGroundColor?: string;
}

const TransitionChart: React.FunctionComponent<TransitionChartProps> = ({
  data,
  chartTitle,
  dataLabel = 'Value',
  dataColor = '#8884d8',
}) => {
  // Transform data to work with Recharts
  const chartData = data.map((value, index) => ({
    index: index,
    value: value,
  }));

  return (
    <div className="space-y-4">
      {chartTitle && (
        <h3 className="text-lg font-semibold text-center">{chartTitle}</h3>
      )}
      <div className="w-full h-[200px] bg-white rounded-lg border p-4">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart
            data={chartData}
            margin={{
              top: 5,
              right: 30,
              left: 20,
              bottom: 5,
            }}
          >
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="index" />
            <YAxis />
            <Tooltip 
              formatter={(value) => [value, dataLabel]}
              labelFormatter={(label) => `Point ${label}`}
            />
            <Line
              type="monotone"
              dataKey="value"
              stroke={dataColor}
              strokeWidth={2}
              dot={{
                fill: dataColor,
                strokeWidth: 2,
                r: 4
              }}
              activeDot={{
                r: 6,
                fill: dataColor
              }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default TransitionChart;
