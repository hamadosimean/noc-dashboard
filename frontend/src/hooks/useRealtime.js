import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

import * as alertsApi from '../api/alerts';

const POLL_INTERVAL_MS = 15000;

// The backend has no WebSocket endpoint yet, so "real time" is approximated with
// short-interval polling — good enough for a NOC dashboard refreshed every 15s.
export const useOpenAlerts = (limit = 20) =>
  useQuery({
    queryKey: ['alerts', 'open', limit],
    queryFn: () => alertsApi.getOpenAlerts(limit),
    refetchInterval: POLL_INTERVAL_MS,
  });

export const useAcknowledgeIncident = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id) => alertsApi.acknowledgeIncident(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alerts'] });
    },
  });
};

export const useResolveIncident = () => {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, notes }) => alertsApi.resolveIncident(id, notes),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alerts'] });
      queryClient.invalidateQueries({ queryKey: ['kpi'] });
    },
  });
};
