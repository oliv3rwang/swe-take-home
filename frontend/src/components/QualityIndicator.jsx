// src/components/QualityIndicator.jsx
import { useMemo } from 'react';

function QualityIndicator({ data, className = '' }) {
  const qualityStats = useMemo(() => {
    if (!data?.length) return null;
    
    const stats = {
      excellent: 0,
      good: 0,
      questionable: 0,
      poor: 0,
      total: data.length
    };
    
    data.forEach(item => {
      stats[item.quality.toLowerCase()]++;
    });
    
    return {
      ...stats,
      percentages: {
        excellent: (stats.excellent / stats.total * 100).toFixed(1),
        good: (stats.good / stats.total * 100).toFixed(1),
        questionable: (stats.questionable / stats.total * 100).toFixed(1),
        poor: (stats.poor / stats.total * 100).toFixed(1)
      }
    };
  }, [data]);

  if (!qualityStats) return null;

  return (
    <div className={`bg-white p-4 rounded-lg shadow-md ${className}`}>
      <h3 className="text-lg font-semibold mb-4">Data Quality Distribution</h3>
      <div className="flex gap-4">
        <QualityBar 
          label="Excellent" 
          percentage={qualityStats.percentages.excellent}
          count={qualityStats.excellent}
          color="bg-green-500"
        />
        <QualityBar 
          label="Good" 
          percentage={qualityStats.percentages.good}
          count={qualityStats.good}
          color="bg-blue-500"
        />
        <QualityBar 
          label="Questionable" 
          percentage={qualityStats.percentages.questionable}
          count={qualityStats.questionable}
          color="bg-yellow-500"
        />
        <QualityBar 
          label="Poor" 
          percentage={qualityStats.percentages.poor}
          count={qualityStats.poor}
          color="bg-red-500"
        />
      </div>
    </div>
  );
}

function QualityBar({ label, percentage, count, color }) {
  return (
    <div className="flex-1">
      <div className="flex justify-between text-sm mb-1">
        <span>{label}</span>
        <span>{percentage}%</span>
      </div>
      <div className="h-2 bg-gray-200 rounded-full">
        <div 
          className={`h-full rounded-full ${color}`} 
          style={{ width: `${percentage}%` }}
        />
      </div>
      <div className="text-xs text-gray-500 mt-1">
        {count} measurements
      </div>
    </div>
  );
}

export default QualityIndicator;