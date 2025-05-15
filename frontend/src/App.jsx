import { useState, useEffect } from 'react';
import Filters from './components/Filters';
import ChartContainer from './components/ChartContainer';
import TrendAnalysis from './components/TrendAnalysis';
import QualityIndicator from './components/QualityIndicator';

function App() {
  const [locations, setLocations] = useState([]);
  const [metrics, setMetrics] = useState([]);
  const [climateData, setClimateData] = useState([]);
  const [trendData, setTrendData] = useState(null);
  const [filters, setFilters] = useState({
    locationId: '',
    startDate: '',
    endDate: '',
    metric: '',
    qualityThreshold: '',
    analysisType: 'raw'
  });
  const [loading, setLoading] = useState(false);

  // Existing useEffect for locations and metrics

  // Updated fetch function to handle different analysis types
  const fetchData = async () => {
    setLoading(true);
    try {
      const queryParams = new URLSearchParams({
        ...(filters.locationId && { location_id: filters.locationId }),
        ...(filters.startDate && { start_date: filters.startDate }),
        ...(filters.endDate && { end_date: filters.endDate }),
        ...(filters.metric && { metric: filters.metric }),
        ...(filters.qualityThreshold && { quality_threshold: filters.qualityThreshold })
      });

      let endpoint = '/api/v1/climate';
      if (filters.analysisType === 'trends') {
        endpoint = '/api/v1/trends';
      } else if (filters.analysisType === 'weighted') {
        endpoint = '/api/v1/summary';
      }

      const response = await fetch(`${endpoint}?${queryParams}`);
      const data = await response.json();
      
      if (filters.analysisType === 'trends') {
        setTrendData(data.data);
      } else {
        setClimateData(data.data);
      }
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-6xl">
      <header className="mb-8 text-center">
        <h1 className="text-4xl font-bold text-eco-primary mb-2">
          EcoVision: Climate Visualizer
        </h1>
        <p className="text-gray-600 italic">
          Transforming climate data into actionable insights for a sustainable future
        </p>
      </header>

      <Filters 
        locations={locations}
        metrics={metrics}
        filters={filters}
        onFilterChange={setFilters}
        onApplyFilters={fetchData}
      />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-8">
        {filters.analysisType === 'trends' ? (
          <TrendAnalysis 
            data={trendData}
            loading={loading}
          />
        ) : (
          <>
            <ChartContainer 
              title="Climate Trends"
              loading={loading}
              chartType="line"
              data={climateData}
              showQuality={true}
            />
            <ChartContainer 
              title="Quality Distribution"
              loading={loading}
              chartType="bar"
              data={climateData}
              showQuality={true}
            />
          </>
        )}
      </div>

      <QualityIndicator 
        data={climateData}
        className="mt-6"
      />
    </div>
  );
}

export default App;