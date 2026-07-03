import apiClient from './client';

export const getSLA = (month, year) =>
  apiClient.get('/sla', { params: { month, year } }).then((r) => r.data);
