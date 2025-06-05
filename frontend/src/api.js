/**
 * API service module for making requests to the backend
 */

const API_BASE_URL = '/api/v1';

/**
 * Helper to build query string from filters object
 * @param {Object} filters
 * @returns {string} - query string starting with '?', or empty string if no filters
 */
const buildQueryString = (filters) => {
  const params = new URLSearchParams();

  Object.entries(filters).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      params.append(key, value);
    }
  });

  const queryString = params.toString();
  return queryString ? `?${queryString}` : '';
};

/**
 * Fetch climate data with optional filters
 * @param {Object} filters - Filter parameters (e.g., { location: 'NY', metric: 'temperature', startDate: '2025-01-01' })
 * @returns {Promise<Object>} - Parsed JSON response
 */
export const getClimateData = async (filters = {}) => {
  try {
    const queryString = buildQueryString(filters);
    const response = await fetch(`${API_BASE_URL}/climate-data${queryString}`, {
      method: 'GET',
      headers: {
        Accept: 'application/json',
      },
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(
        `Failed to fetch climate data: ${response.status} ${errorText}`
      );
    }

    return await response.json();
  } catch (error) {
    console.error('API Error [getClimateData]:', error);
    throw error;
  }
};

/**
 * Fetch all available locations
 * @returns {Promise<Object[]>} - Parsed JSON array of locations
 */
export const getLocations = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/locations`, {
      method: 'GET',
      headers: {
        Accept: 'application/json',
      },
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(
        `Failed to fetch locations: ${response.status} ${errorText}`
      );
    }

    return await response.json();
  } catch (error) {
    console.error('API Error [getLocations]:', error);
    throw error;
  }
};

/**
 * Fetch all available metrics
 * @returns {Promise<Object[]>} - Parsed JSON array of metrics
 */
export const getMetrics = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/metrics`, {
      method: 'GET',
      headers: {
        Accept: 'application/json',
      },
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(
        `Failed to fetch metrics: ${response.status} ${errorText}`
      );
    }

    return await response.json();
  } catch (error) {
    console.error('API Error [getMetrics]:', error);
    throw error;
  }
};

/**
 * Fetch climate summary statistics with optional filters
 * @param {Object} filters - Filter parameters (e.g., { location: 'CA', startDate: '2025-01-01', endDate: '2025-03-01' })
 * @returns {Promise<Object>} - Parsed JSON response
 */
export const getClimateSummary = async (filters = {}) => {
  try {
    const queryString = buildQueryString(filters);
    const response = await fetch(
      `${API_BASE_URL}/climate-summary${queryString}`,
      {
        method: 'GET',
        headers: {
          Accept: 'application/json',
        },
      }
    );

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(
        `Failed to fetch climate summary: ${response.status} ${errorText}`
      );
    }

    return await response.json();
  } catch (error) {
    console.error('API Error [getClimateSummary]:', error);
    throw error;
  }
};
