import React from "react";
import { useNavigate } from "react-router-dom";
import { AlertTriangle, CheckCircle2, Clock, Signal } from "lucide-react";
import KPICard from "../components/KPICard";
import Card from "../components/Card";
import WeeklyBar from "../components/charts/WeeklyBar";
import MTTRDonut from "../components/charts/MTTRDonut";
import BurkinaFasoMap from "../components/map/BurkinaFasoMap";
import LocalityBulletList from "../components/map/LocalityBulletList";
import {
  useKpiSummary,
  useKpiTrend,
  useKpiCauses,
  useKpiLocalitiesMap,
} from "../hooks/useKPI";

const ChartLoading = () => (
  <div
    className="flex h-64 items-center justify-center text-sm"
    style={{ color: "var(--color-text-muted)" }}
  >
    Chargement…
  </div>
);

const GlobalView = () => {
  const navigate = useNavigate();
  const { data: summary, isLoading: summaryLoading } = useKpiSummary();
  const { data: trend, isLoading: trendLoading } = useKpiTrend(6);
  const { data: causes, isLoading: causesLoading } = useKpiCauses();
  const { data: localities = [], isLoading: mapLoading } =
    useKpiLocalitiesMap();

  const kpi = summary?.kpi;
  const delta = summary?.vs_previous_month;

  const goToLocality = (localityId) =>
    navigate("/locality", { state: { localityId } });

  return (
    <div className="space-y-6">
      <div>
        <h2
          className="text-xl font-bold"
          style={{ color: "var(--color-text-primary)" }}
        >
          Vue Globale
        </h2>
        <p className="text-sm" style={{ color: "var(--color-text-secondary)" }}>
          Supervision H24 du réseau national —{" "}
          {kpi ? `${kpi.total_incidents} incidents` : "…"} ce mois-ci
        </p>
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
        <KPICard
          title="Total Incidents"
          value={kpi?.total_incidents}
          icon={AlertTriangle}
          trend={
            delta
              ? `${delta.incidents_delta >= 0 ? "+" : ""}${delta.incidents_delta}`
              : null
          }
          trendDirection={
            delta ? (delta.incidents_delta >= 0 ? "up" : "down") : null
          }
          sentiment={
            delta ? (delta.incidents_delta <= 0 ? "good" : "bad") : "neutral"
          }
          loading={summaryLoading}
        />
        <KPICard
          title="Disponibilité Réseau"
          value={kpi ? `${kpi.network_availability_pct}%` : null}
          icon={Signal}
          trend={
            delta
              ? `${delta.availability_delta >= 0 ? "+" : ""}${delta.availability_delta}%`
              : null
          }
          trendDirection={
            delta ? (delta.availability_delta >= 0 ? "up" : "down") : null
          }
          sentiment={
            delta ? (delta.availability_delta >= 0 ? "good" : "bad") : "neutral"
          }
          loading={summaryLoading}
        />
        <KPICard
          title="Taux de Résolution"
          value={kpi ? `${kpi.resolution_rate_pct}%` : null}
          icon={CheckCircle2}
          loading={summaryLoading}
        />
        <KPICard
          title="MTTR Moyen"
          value={kpi ? `${kpi.avg_mttr_minutes} min` : null}
          icon={Clock}
          loading={summaryLoading}
        />
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-5">
        <Card
          title="Carte de Supervision"
          subtitle="Cliquez une localité pour la retrouver dans Vue par Localité"
          className="lg:col-span-3"
        >
          {mapLoading ? (
            <ChartLoading />
          ) : (
            <BurkinaFasoMap
              localities={localities}
              onSelect={goToLocality}
              height="clamp(360px, calc(100vh - 480px), 680px)"
            />
          )}
        </Card>
        <Card
          title="Localités"
          subtitle="Triées par volume d'incidents"
          className="lg:col-span-2"
        >
          {mapLoading ? (
            <ChartLoading />
          ) : (
            <LocalityBulletList
              localities={localities}
              onSelect={goToLocality}
              maxHeight="clamp(300px, calc(100vh - 480px), 640px)"
            />
          )}
        </Card>
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <Card title="Évolution Mensuelle" subtitle="6 derniers mois">
          <div className="h-64">
            {trendLoading ? <ChartLoading /> : <WeeklyBar points={trend} />}
          </div>
        </Card>
        <Card title="Répartition des incidents par cause">
          <div className="h-64">
            {causesLoading ? <ChartLoading /> : <MTTRDonut causes={causes} />}
          </div>
        </Card>
      </div>
    </div>
  );
};

export default GlobalView;
