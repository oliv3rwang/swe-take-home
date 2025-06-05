// src/components/WeightedSummary.jsx
import React from 'react';
import { Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

function capitalize(str) {
  return str?.charAt(0).toUpperCase() + str?.slice(1);
}

function WeightedSummary({ data, loading }) {
  if (loading) {
    return (
      <div className="bg-white p-4 rounded-lg shadow-md animate-pulse h-96" />
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className="bg-white p-4 rounded-lg shadow-md h-96">
        <p className="text-gray-500">No weighted summary data available.</p>
      </div>
    );
  }

  // Build table rows from data
  const tableRows = data.map((item) => ({
    metric: capitalize(item.metric),
    unit: item.unit,
    weightedMin: parseFloat(item.weighted_min?.toFixed(2)),
    weightedMax: parseFloat(item.weighted_max?.toFixed(2)),
    weightedAvg: parseFloat(item.weighted_avg?.toFixed(2))
  }));

  // For each metric, prepare chart data for quality distribution
  const chartConfigs = data.map((item, idx) => {
    const labels = ['Excellent', 'Good', 'Questionable', 'Poor'];
    const counts = [
      item.quality_distribution?.excellent || 0,
      item.quality_distribution?.good || 0,
      item.quality_distribution?.questionable || 0,
      item.quality_distribution?.poor || 0
    ];
    // Generate a consistent HSL color for each metric based on index
    const hue = Math.round((idx * 360) / data.length);
    const bgColor = `hsla(${hue}, 70%, 50%, 0.7)`;
    const borderColor = `hsla(${hue}, 70%, 50%, 1)`;

    return {
      metricName: capitalize(item.metric),
      chartData: {
        labels,
        datasets: [
          {
            label: 'Count',
            data: counts,
            backgroundColor: labels.map(() => bgColor),
            borderColor: labels.map(() => borderColor),
            borderWidth: 1
          }
        ]
      },
      chartOptions: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          title: {
            display: true,
            text: `Quality Distribution: ${capitalize(item.metric)}`
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            title: {
              display: true,
              text: 'Count'
            }
          }
        }
      }
    };
  });

  return (
    <div className="space-y-6">
      {/* Summary Table */}
      <div className="bg-white p-4 rounded-lg shadow-md overflow-auto">
        <h2 className="text-xl font-semibold text-eco-primary mb-4">
          Weighted Summary Statistics
        </h2>
        <table className="min-w-full border-collapse">
          <thead>
            <tr className="bg-gray-100">
              <th className="px-4 py-2 border">Metric</th>
              <th className="px-4 py-2 border">Weighted Min</th>
              <th className="px-4 py-2 border">Weighted Max</th>
              <th className="px-4 py-2 border">Weighted Avg</th>
              <th className="px-4 py-2 border">Unit</th>
            </tr>
          </thead>
          <tbody>
            {tableRows.map((row) => (
              <tr key={row.metric} className="hover:bg-gray-50">
                <td className="border px-4 py-2">{row.metric}</td>
                <td className="border px-4 py-2">{row.weightedMin}</td>
                <td className="border px-4 py-2">{row.weightedMax}</td>
                <td className="border px-4 py-2">{row.weightedAvg}</td>
                <td className="border px-4 py-2 capitalize">{row.unit}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Quality Distribution Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {chartConfigs.map(({ metricName, chartData, chartOptions }) => (
          <div key={metricName} className="bg-white p-4 rounded-lg shadow-md h-96">
            <div className="h-4/5">
              <Bar data={chartData} options={chartOptions} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default WeightedSummary;
