# EcoVision: Climate Visualizer Frontend

Luckily, one of your coworkers helped build this frontend for the EcoVision Climate Visualizer application. 

They built it with today's modern stacks: React, Vite, and TailwindCSS. The visualization components are pre-implemented, but they don't quite know how to wire it all up together.

<small>Note: Of course, you're more than welcome to start from scratch, if their boilerplate is not up to your standard...</small>

## Getting Started

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

This will start the frontend application at http://localhost:3000.

## Project Structure

- `src/App.jsx` - Main application component, handles state and data flow
- `src/api.js` - API service functions (needs implementation)
- `src/components/` - React components
  - `ChartContainer.jsx` - Pre-built chart visualization component
  - `Filters.jsx` - Filter UI component (needs implementation)
  - `QualityIndicator.jsx` - Data quality distribution display
  - `TrendAnalysis.jsx` - Trend and anomaly visualization

## Your Tasks

Focus on implementing:

1. API Integration
   - Implement the API service functions in `api.js`
   - Handle API responses and errors appropriately
   - Map API data to the component props

2. Filters Component
   - Design and implement the `Filters.jsx` component from scratch
   - Create an intuitive UI for users to select locations, metrics, date ranges, etc.
   - Implement state management for filters
   - Ensure responsive design and good user experience

3. State Management & Data Flow
   - Connect the API with the UI components
   - Manage loading states during API calls
   - Update visualizations when new data arrives
   - Handle empty states and error conditions

## Pre-implemented Features

The following features are already implemented for you:

- Chart visualizations (line and bar charts)
- Quality-weighted data display
- Trend analysis visualization
- Data quality indicators
- Core responsive layout and styling
- Loading and empty states

## Component Props

### ChartContainer
```jsx
<ChartContainer 
  title="string"          // Chart title
  loading={boolean}       // Loading state
  chartType="line"|"bar"  // Chart type
  data={array}           // Climate data array
  showQuality={boolean}  // Whether to show quality indicators
/>
```

### QualityIndicator
```jsx
<QualityIndicator 
  data={array}          // Climate data array
  className="string"    // Optional CSS classes
/>
```

### TrendAnalysis
```jsx
<TrendAnalysis 
  data={object}         // Trend analysis data
  loading={boolean}     // Loading state
/>
```

### Filters
```jsx
<Filters 
  locations={array}     // Available locations
  metrics={array}       // Available metrics
  filters={object}      // Current filter values
  onFilterChange={func} // Filter change handler
  onApplyFilters={func} // Apply filters handler
/>
```

## Dependencies

- React - UI library
- Vite - Build tool and dev server
- TailwindCSS - Utility-first CSS framework
- Chart.js and react-chartjs-2 - Pre-configured for visualizations
- React DatePicker - Date selection component for date inputs

## API Integration Example

```javascript
// Example of fetching climate data
const fetchClimateData = async (filters) => {
  try {
    const queryParams = new URLSearchParams({
      location_id: filters.locationId,
      start_date: filters.startDate,
      end_date: filters.endDate,
      metric: filters.metric,
      quality_threshold: filters.qualityThreshold
    });

    const response = await fetch(`/api/v1/climate?${queryParams}`);
    const data = await response.json();
    
    return data;
  } catch (error) {
    console.error('Error fetching climate data:', error);
    throw error;
  }
};
```

## Implementation Notes

- Design an intuitive and user-friendly filter component
- Focus on clean, maintainable API integration code
- Implement proper error handling for API calls
- Ensure the UI is responsive and works well on different devices
- Consider edge cases in data handling (empty results, errors, etc.)
- Follow REST API best practices
- Use TypeScript if you prefer (optional)