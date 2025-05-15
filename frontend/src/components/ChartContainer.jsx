// src/components/ChartContainer.jsx
import { Line, Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend
);

// Utility function to generate random colors
const getRandomColor = (opacity = 1) => {
  const r = Math.floor(Math.random() * 255);
  const g = Math.floor(Math.random() * 255);
  const b = Math.floor(Math.random() * 255);
  return `rgba(${r}, ${g}, ${b}, ${opacity})`;
};

// Quality color mapping
const qualityColors = {
  excellent: 'rgba(34, 197, 94, 0.7)',  // green
  good: 'rgba(59, 130, 246, 0.7)',      // blue
  questionable: 'rgba(234, 179, 8, 0.7)', // yellow
  poor: 'rgba(239, 68, 68, 0.7)'        // red
};

function ChartContainer({ title, loading, chartType, data, showQuality = false }) {
  if (loading) {
    return (
      <div className="bg-white p-4 rounded-lg shadow-md h-96">
        <h2 className="text-xl font-semibold text-eco-primary mb-4">{title}</h2>
        <div className="flex items-center justify-center h-full">
          <p className="text-gray-500">Loading data...</p>
        </div>
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className="bg-white p-4 rounded-lg shadow-md h-96">
        <h2 className="text-xl font-semibold text-eco-primary mb-4">{title}</h2>
        <div className="flex items-center justify-center h-full">
          <p className="text-gray-500">No data available. Please apply filters to see visualizations.</p>
        </div>
      </div>
    );
  }

  // Prepare chart data
  const locations = [...new Set(data.map(item => item.location_name))];
  const dates = [...new Set(data.map(item => item.date))].sort();
  
  const datasets = locations.map(location => {
    const locationData = data.filter(item => item.location_name === location);
    const color = getRandomColor();
    
    return {
      label: location,
      data: dates.map(date => {
        const point = locationData.find(item => item.date === date);
        return point ? point.value : null;
      }),
      borderColor: showQuality ? locationData.map(item => qualityColors[item.quality]) : color,
      backgroundColor: showQuality ? locationData.map(item => qualityColors[item.quality]) : color,
      pointBackgroundColor: showQuality ? locationData.map(item => qualityColors[item.quality]) : color,
      borderWidth: 2,
      tension: 0.1
    };
  });

  const chartData = {
    labels: dates,
    datasets
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'top',
      },
      tooltip: {
        callbacks: {
          afterLabel: function(context) {
            if (showQuality) {
              const dataPoint = data.find(item => 
                item.location_name === context.dataset.label && 
                item.date === context.label
              );
              return dataPoint ? `Quality: ${dataPoint.quality}` : '';
            }
          }
        }
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        title: {
          display: true,
          text: data[0]?.unit || 'Value'
        }
      },
      x: {
        title: {
          display: true,
          text: 'Date'
        }
      }
    }
  };

  return (
    <div className="bg-white p-4 rounded-lg shadow-md h-96">
      <h2 className="text-xl font-semibold text-eco-primary mb-4">{title}</h2>
      <div className="h-5/6">
        {chartType === 'line' ? (
          <Line data={chartData} options={chartOptions} />
        ) : (
          <Bar data={chartData} options={chartOptions} />
        )}
      </div>
    </div>
  );
}

export default ChartContainer;