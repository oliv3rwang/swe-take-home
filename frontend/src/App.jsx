// src/App.jsx
import React, { useState, useEffect } from 'react';
import Filters from './components/Filters';
import ChartContainer from './components/ChartContainer';
import TrendAnalysis from './components/TrendAnalysis';
import QualityIndicator from './components/QualityIndicator';
import WeightedSummary from './components/WeightedSummary';

function App() {
  const [locations, setLocations] = useState([]);
  const [metrics, setMetrics] = useState([]);
  const [climateData, setClimateData] = useState([]);
  const [trendData, setTrendData] = useState([]);
  const [filters, setFilters] = useState({
    locationId: '',
    startDate: '',
    endDate: '',
    metric: '',
    qualityThreshold: '',
    analysisType: 'raw'
  });
  const [loading, setLoading] = useState(false);

  // Fetch dropdown options on mount
  useEffect(() => {
    async function fetchOptions() {
      try {
        const [locs, mets] = await Promise.all([
          fetch('/api/v1/locations').then((res) => res.json()),
          fetch('/api/v1/metrics').then((res) => res.json())
        ]);
        setLocations(locs.data);
        setMetrics(mets.data);
      } catch (err) {
        console.error('Error fetching dropdown options:', err);
      }
    }
    fetchOptions();
  }, []);

  // Whenever analysisType changes, clear previously fetched data
  useEffect(() => {
    setClimateData([]);
    setTrendData([]);
  }, [filters.analysisType]);

  // Fetch data based on analysisType
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
        setTrendData(data);
        setClimateData([]);
      } else {
        setClimateData(data.data || []);
        setTrendData([]);
      }
    } catch (error) {
      console.error('Error fetching data:', error);
      setClimateData([]);
      setTrendData([]);
    } finally {
      setLoading(false);
    }
  };

  const gridColsClass = filters.analysisType === 'raw'
    ? 'grid-cols-1 lg:grid-cols-2'
    : 'grid-cols-1';

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

      <div className={`grid ${gridColsClass} gap-6 mt-8`}>
        {filters.analysisType === 'trends' ? (
          <TrendAnalysis
            data={trendData}
            loading={loading}
          />
        ) : filters.analysisType === 'weighted' ? (
          <WeightedSummary
            data={climateData}
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
