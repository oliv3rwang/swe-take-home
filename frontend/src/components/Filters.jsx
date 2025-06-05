// src/components/Filters.jsx
import React from 'react';

const DEFAULT_LOCATIONS = [
  { id: 'Irvine', name: 'Irvine' },
  { id: 'London', name: 'London' },
  { id: 'Tokyo', name: 'Tokyo' }
];

const DEFAULT_METRICS = [
  { id: 'humidity', name: 'Humidity' },
  { id: 'precipitation', name: 'Precipitation' },
  { id: 'temperature', name: 'Temperature' }
];

function Filters({ filters, onFilterChange, onApplyFilters }) {
  // When the user changes any field, we propagate it upward
  const handleChange = (e) => {
    const { name, value } = e.target;
    onFilterChange({
      ...filters,
      [name]: value
    });
  };

  const handleReset = () => {
    onFilterChange({ ...DEFAULT_FILTERS });
  };

  return (
    <div className="bg-white p-4 rounded-lg shadow-md">
      <h2 className="text-xl font-semibold text-eco-primary mb-4">Filter Data</h2>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Location dropdown (hard-coded) */}
        <div>
          <label htmlFor="locationId" className="block text-sm font-medium text-gray-700">
            Location
          </label>
          <select
            id="locationId"
            name="locationId"
            value={filters.locationId}
            onChange={handleChange}
            className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500"
          >
            <option value="">All locations</option>
            {DEFAULT_LOCATIONS.map((loc) => (
              <option key={loc.id} value={loc.id}>
                {loc.name}
              </option>
            ))}
          </select>
        </div>

        {/* Metric dropdown (hard-coded) */}
        <div>
          <label htmlFor="metric" className="block text-sm font-medium text-gray-700">
            Metric
          </label>
          <select
            id="metric"
            name="metric"
            value={filters.metric}
            onChange={handleChange}
            className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500"
          >
            <option value="">All metrics</option>
            {DEFAULT_METRICS.map((met) => (
              <option key={met.id} value={met.id}>
                {met.name}
              </option>
            ))}
          </select>
        </div>

        {/* Start date picker */}
        <div>
          <label htmlFor="startDate" className="block text-sm font-medium text-gray-700">
            Start Date
          </label>
          <input
            type="date"
            id="startDate"
            name="startDate"
            value={filters.startDate}
            onChange={handleChange}
            className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500"
          />
        </div>

        {/* End date picker */}
        <div>
          <label htmlFor="endDate" className="block text-sm font-medium text-gray-700">
            End Date
          </label>
          <input
            type="date"
            id="endDate"
            name="endDate"
            value={filters.endDate}
            onChange={handleChange}
            className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500"
          />
        </div>

        {/* Quality threshold dropdown */}
        <div>
          <label htmlFor="qualityThreshold" className="block text-sm font-medium text-gray-700">
            Quality Threshold
          </label>
          <select
            id="qualityThreshold"
            name="qualityThreshold"
            value={filters.qualityThreshold}
            onChange={handleChange}
            className="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500"
          >
            <option value="">Any quality</option>
            <option value="excellent">Excellent</option>
            <option value="good">Good</option>
            <option value="questionable">Questionable</option>
            <option value="poor">Poor</option>
          </select>
        </div>

        {/* Analysis type radio group */}
        <div className="md:col-span-2">
          <span className="block text-sm font-medium text-gray-700">Analysis Type</span>
          <div className="mt-1 flex space-x-4">
            <label className="inline-flex items-center">
              <input
                type="radio"
                name="analysisType"
                value="raw"
                checked={filters.analysisType === 'raw'}
                onChange={handleChange}
                className="form-radio text-indigo-600"
              />
              <span className="ml-2 text-gray-700">Raw</span>
            </label>
            <label className="inline-flex items-center">
              <input
                type="radio"
                name="analysisType"
                value="trends"
                checked={filters.analysisType === 'trends'}
                onChange={handleChange}
                className="form-radio text-indigo-600"
              />
              <span className="ml-2 text-gray-700">Trends</span>
            </label>
            <label className="inline-flex items-center">
              <input
                type="radio"
                name="analysisType"
                value="weighted"
                checked={filters.analysisType === 'weighted'}
                onChange={handleChange}
                className="form-radio text-indigo-600"
              />
              <span className="ml-2 text-gray-700">Weighted Summary</span>
            </label>
          </div>
        </div>
      </div>

      {/* “Apply Filters” button */}
      <div className="mt-4 text-right space-x-2">
        <button
          type="button"
          onClick={handleReset}
          className="px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500"
        >
          Reset
        </button>
        <button
          onClick={onApplyFilters}
          className="px-4 py-2 bg-eco-primary text-white rounded-md hover:bg-eco-primary-dark focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-eco-primary"
        >
          Apply Filters
        </button>
      </div>
    </div>
  );
}

export default Filters;
