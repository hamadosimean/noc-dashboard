import apiClient from "./client";

export const getSummary = (month, year) =>
  apiClient
    .get("/kpi/summary", { params: { month, year } })
    .then((r) => r.data);

export const getLocalities = (month, year, limit = 10) =>
  apiClient
    .get("/kpi/localities", { params: { month, year, limit } })
    .then((r) => r.data);

export const getNodes = (month, year, localityId, limit = 10) =>
  apiClient
    .get("/kpi/nodes", {
      params: { month, year, locality_id: localityId, limit },
    })
    .then((r) => r.data);

export const getRecurrent = (month, year, minCount = 3) =>
  apiClient
    .get("/kpi/recurrent", { params: { month, year, min_count: minCount } })
    .then((r) => r.data);

export const getTrend = (month, year, months = 6) =>
  apiClient
    .get("/kpi/trend", { params: { month, year, months } })
    .then((r) => r.data);

export const getHourDistribution = (month, year) =>
  apiClient
    .get("/kpi/hour-distribution", { params: { month, year } })
    .then((r) => r.data);

export const getLocalityNodes = (localityId, month, year) =>
  apiClient
    .get(`/locality/${localityId}/nodes`, { params: { month, year } })
    .then((r) => r.data);

export const getCauses = (month, year) =>
  apiClient.get('/kpi/causes', { params: { month, year } }).then((r) => r.data);

export const getLocalitiesMap = (month, year) =>
  apiClient.get('/kpi/localities/map', { params: { month, year } }).then((r) => r.data);
