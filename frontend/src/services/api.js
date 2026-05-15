import axios from "axios";

const BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 30000,
  headers: { "Content-Type": "application/json" },
});

// ── Players ────────────────────────────────────────────────────
export const getPlayers = (params = {}) =>
  api.get("/players/", { params }).then((r) => r.data);

export const getPlayer = (id) =>
  api.get(`/players/${id}`).then((r) => r.data);

export const getPlayerRadar = (id) =>
  api.get(`/players/${id}/radar-stats`).then((r) => r.data);

export const getPlayerShotZones = (id) =>
  api.get(`/players/${id}/shot-zones`).then((r) => r.data);

// ── Teams ──────────────────────────────────────────────────────
export const getTeams = (params = {}) =>
  api.get("/teams/", { params }).then((r) => r.data);

export const getTeam = (id) =>
  api.get(`/teams/${id}`).then((r) => r.data);

export const getTeamComparison = () =>
  api.get("/teams/1/stats-comparison").then((r) => r.data);

// ── Shots ──────────────────────────────────────────────────────
export const getShotChartData = (playerId, limit = 500) =>
  api.get("/shots/chart-data", { params: { player_id: playerId, limit } }).then((r) => r.data);

export const getLeagueShotSummary = () =>
  api.get("/shots/league-summary").then((r) => r.data);

// ── Analytics ──────────────────────────────────────────────────
export const predictShotProbability = (data) =>
  api.post("/analytics/shot-probability", data).then((r) => r.data);

export const getPlayerSimilarity = (data) =>
  api.post("/analytics/player-similarity", data).then((r) => r.data);

export const getModelMetrics = () =>
  api.get("/analytics/model-metrics").then((r) => r.data);

export const getLeaderboard = (stat = "points_per_game", limit = 10) =>
  api.get("/analytics/leaderboard", { params: { stat, limit } }).then((r) => r.data);

export const predictWinProbability = (data) =>
  api.post("/analytics/win-probability", data).then((r) => r.data);

export const predictPlayerPerformance = (data) =>
  api.post("/analytics/player-performance", data).then((r) => r.data);

export const getClusterData = () =>
  api.get("/analytics/player-similarity/clusters").then((r) => r.data);

export default api;
