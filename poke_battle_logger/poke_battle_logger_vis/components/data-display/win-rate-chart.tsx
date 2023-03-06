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

interface WinRateChartProps {
  win_rates: number[];
}

const WinRateChart: React.FunctionComponent<WinRateChartProps> = ({
  win_rates,
}) => {
  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: '勝率推移(シーズン3)',
      },
    },
    maintainAspectRatio: true,
    aspectRatio: 2
  };

  // label is index of win_rates(0,1,2,...)
  const labels = win_rates.map((_, index) => index);
  const data = {
    labels,
    datasets: [
      {
        label: '勝率',
        data: win_rates,
        borderColor: 'rgb(255, 99, 132)',
        backgroundColor: 'rgba(255, 99, 132, 0.5)',
      },
    ],
  };

  return (
    <div style={{ position: "relative", height: "auto", width: "35vw" }}>
      <Line options={options} data={data} />
    </div>
  );
};

export default WinRateChart;
