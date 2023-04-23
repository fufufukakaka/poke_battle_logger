import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Line } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

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
  dataLabel,
  dataColor,
  dataBackGroundColor,
}) => {
  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: chartTitle,
      },
    },
    maintainAspectRatio: true,
    aspectRatio: 2
  };

  // label is index of win_rates(0,1,2,...)
  const labels = data.map((_, index) => index);
  const chartData = {
    labels,
    datasets: [
      {
        label: dataLabel,
        data: data,
        borderColor: dataColor,
        backgroundColor: dataBackGroundColor,
      },
    ],
  };

  return (
    <div style={{ position: "relative", height: "auto", width: "35vw" }}>
      <Line options={options} data={chartData} />
    </div>
  );
};

export default TransitionChart;
