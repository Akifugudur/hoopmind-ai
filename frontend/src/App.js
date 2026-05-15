import React, { useState, useEffect, useCallback } from "react";
import {
  BarChart, Bar, LineChart, Line, RadarChart, Radar, PolarGrid,
  PolarAngleAxis, PolarRadiusAxis, ScatterChart, Scatter,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  ResponsiveContainer, Cell, ReferenceLine,
} from "recharts";
import * as api from "./services/api";
import "./App.css";

// ── Color palette ─────────────────────────────────────────────────
const C = {
  bg:       "#0a0e1a",
  surface:  "#111827",
  card:     "#1a2235",
  border:   "#1e2d45",
  accent:   "#3b82f6",
  accent2:  "#8b5cf6",
  success:  "#22c55e",
  warning:  "#f59e0b",
  danger:   "#ef4444",
  text:     "#f1f5f9",
  muted:    "#64748b",
  made:     "#22c55e",
  missed:   "#ef4444",
};

const TABS = ["Dashboard", "Shot Analytics", "Player Explorer", "Similarity Engine", "Model Performance"];

// ── Helpers ───────────────────────────────────────────────────────
const StatCard = ({ label, value, sub, color = C.accent, icon }) => (
  <div style={{
    background: C.card, border: `1px solid ${C.border}`,
    borderRadius: 12, padding: "20px 24px",
    borderLeft: `3px solid ${color}`,
  }}>
    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
      <div>
        <div style={{ color: C.muted, fontSize: 12, fontWeight: 500, textTransform: "uppercase", letterSpacing: 1 }}>{label}</div>
        <div style={{ color: C.text, fontSize: 28, fontWeight: 700, marginTop: 4 }}>{value}</div>
        {sub && <div style={{ color: C.muted, fontSize: 12, marginTop: 4 }}>{sub}</div>}
      </div>
      {icon && <div style={{ fontSize: 28, opacity: 0.6 }}>{icon}</div>}
    </div>
  </div>
);

const SectionTitle = ({ children, sub }) => (
  <div style={{ marginBottom: 20 }}>
    <h2 style={{ color: C.text, fontSize: 20, fontWeight: 700, margin: 0 }}>{children}</h2>
    {sub && <div style={{ color: C.muted, fontSize: 13, marginTop: 4 }}>{sub}</div>}
  </div>
);

const Loader = () => (
  <div style={{ display: "flex", alignItems: "center", justifyContent: "center", padding: 60, color: C.muted }}>
    <div style={{ textAlign: "center" }}>
      <div style={{ fontSize: 32, marginBottom: 12 }}>⏳</div>
      <div>Loading data...</div>
    </div>
  </div>
);

const Badge = ({ children, color = C.accent }) => (
  <span style={{
    background: color + "22", color, border: `1px solid ${color}44`,
    borderRadius: 6, padding: "2px 8px", fontSize: 11, fontWeight: 600,
  }}>{children}</span>
);

// ── NBA Court SVG ─────────────────────────────────────────────────
const CourtBackground = () => (
  <g>
    {/* Court outline */}
    <rect x="0" y="0" width="500" height="470" fill="#1a2235" rx="4"/>
    {/* Paint */}
    <rect x="170" y="290" width="160" height="145" fill="none" stroke="#2d4a7a" strokeWidth="1.5"/>
    {/* Free throw circle */}
    <ellipse cx="250" cy="290" rx="60" ry="60" fill="none" stroke="#2d4a7a" strokeWidth="1.5"/>
    {/* Basket */}
    <circle cx="250" cy="420" r="7.5" fill="none" stroke="#e8a838" strokeWidth="2"/>
    <line x1="220" y1="435" x2="280" y2="435" stroke="#2d4a7a" strokeWidth="1.5"/>
    {/* 3PT arc */}
    <path d="M 60 435 L 60 280 A 210 210 0 0 1 440 280 L 440 435" fill="none" stroke="#2d4a7a" strokeWidth="1.5"/>
    {/* Center label */}
    <text x="250" y="60" textAnchor="middle" fill="#2d4a7a" fontSize="11" fontFamily="sans-serif">HOOPMIND AI</text>
  </g>
);

// Map shot coords to SVG (court is 500x470, basket at center-bottom ~250,420)
const courtX = (x) => 250 + x * 10;
const courtY = (y) => 420 - (y - 5.25) * 10;

// ── TAB 1: Dashboard ─────────────────────────────────────────────
const DashboardTab = () => {
  const [players, setPlayers] = useState([]);
  const [teams, setTeams] = useState([]);
  const [leaderboard, setLeaderboard] = useState([]);
  const [shotSummary, setShotSummary] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeStat, setActiveStat] = useState("points_per_game");

  const STATS = [
    { key: "points_per_game", label: "PPG" },
    { key: "assists_per_game", label: "APG" },
    { key: "rebounds_per_game", label: "RPG" },
    { key: "player_efficiency_rating", label: "PER" },
    { key: "true_shooting_pct", label: "TS%" },
  ];

  useEffect(() => {
    Promise.all([
      api.getPlayers({ page_size: 5, sort_by: "points_per_game" }),
      api.getTeams({ sort_by: "wins" }),
      api.getLeaderboard(activeStat, 10),
      api.getLeagueShotSummary(),
    ]).then(([p, t, lb, ss]) => {
      setPlayers(p.items || []);
      setTeams(t.items || []);
      setLeaderboard(lb || []);
      setShotSummary(ss || []);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  useEffect(() => {
    api.getLeaderboard(activeStat, 10).then(setLeaderboard);
  }, [activeStat]);

  if (loading) return <Loader />;

  const topTeam = teams[0];
  const totalPlayers = players.length;

  return (
    <div>
      {/* Hero stats */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 16, marginBottom: 28 }}>
        <StatCard label="NBA Teams" value="30" sub="2023-24 Season" icon="🏀" color={C.accent} />
        <StatCard label="Players Tracked" value="40+" sub="Active Roster" icon="👤" color={C.accent2} />
        <StatCard label="Shots Analyzed" value="60K+" sub="Season shot logs" icon="🎯" color={C.success} />
        <StatCard label="ML Models" value="3" sub="LR · RF · XGBoost" icon="🤖" color={C.warning} />
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 24, marginBottom: 28 }}>
        {/* Leaderboard */}
        <div style={{ background: C.card, border: `1px solid ${C.border}`, borderRadius: 12, padding: 24 }}>
          <div style={{ display: "flex", gap: 8, marginBottom: 16, flexWrap: "wrap" }}>
            {STATS.map(s => (
              <button key={s.key} onClick={() => setActiveStat(s.key)}
                style={{
                  background: activeStat === s.key ? C.accent : "transparent",
                  color: activeStat === s.key ? "#fff" : C.muted,
                  border: `1px solid ${activeStat === s.key ? C.accent : C.border}`,
                  borderRadius: 6, padding: "4px 12px", fontSize: 12, cursor: "pointer",
                }}>
                {s.label}
              </button>
            ))}
          </div>
          <SectionTitle sub="Top 10 Players">League Leaderboard</SectionTitle>
          {leaderboard.map((p, i) => (
            <div key={p.player_id} style={{
              display: "flex", alignItems: "center", padding: "8px 0",
              borderBottom: `1px solid ${C.border}`,
            }}>
              <div style={{ color: C.muted, width: 24, fontSize: 12 }}>#{p.rank}</div>
              <div style={{ flex: 1 }}>
                <div style={{ color: C.text, fontSize: 13, fontWeight: 600 }}>{p.player_name}</div>
                <div style={{ color: C.muted, fontSize: 11 }}>{p.team} · {p.position}</div>
              </div>
              <div style={{ color: C.accent, fontWeight: 700, fontSize: 16 }}>
                {typeof p.value === "number" && p.value < 1 ? (p.value * 100).toFixed(1) + "%" : p.value}
              </div>
            </div>
          ))}
        </div>

        {/* Shot zone chart */}
        <div style={{ background: C.card, border: `1px solid ${C.border}`, borderRadius: 12, padding: 24 }}>
          <SectionTitle sub="FG% by court zone">League Shot Distribution</SectionTitle>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={shotSummary} margin={{ top: 0, right: 10, left: -20, bottom: 60 }}>
              <CartesianGrid strokeDasharray="3 3" stroke={C.border} />
              <XAxis dataKey="zone" stroke={C.muted} tick={{ fill: C.muted, fontSize: 10 }} angle={-30} textAnchor="end" />
              <YAxis stroke={C.muted} tick={{ fill: C.muted, fontSize: 11 }}
                tickFormatter={v => (v * 100).toFixed(0) + "%"} />
              <Tooltip
                contentStyle={{ background: C.surface, border: `1px solid ${C.border}`, borderRadius: 8 }}
                labelStyle={{ color: C.text }}
                formatter={(v, n) => n === "fg_pct" ? [(v * 100).toFixed(1) + "%", "FG%"] : [v, n]} />
              <Bar dataKey="fg_pct" name="FG%" radius={[4, 4, 0, 0]}>
                {shotSummary.map((_, i) => (
                  <Cell key={i} fill={[C.accent, C.accent2, C.success, C.warning, C.danger, "#ec4899"][i % 6]} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Teams table */}
      <div style={{ background: C.card, border: `1px solid ${C.border}`, borderRadius: 12, padding: 24 }}>
        <SectionTitle sub="Season standings — sorted by wins">Team Standings</SectionTitle>
        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
            <thead>
              <tr style={{ color: C.muted, fontSize: 11, textTransform: "uppercase", letterSpacing: 1 }}>
                {["#", "Team", "Conf", "W", "L", "Win%", "OffRtg", "DefRtg", "NetRtg", "Pace"].map(h => (
                  <th key={h} style={{ padding: "8px 12px", textAlign: h === "Team" ? "left" : "center", fontWeight: 500 }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {teams.slice(0, 15).map((t, i) => (
                <tr key={t.id} style={{
                  borderTop: `1px solid ${C.border}`,
                  background: i % 2 === 0 ? "transparent" : "#ffffff05",
                }}>
                  <td style={{ padding: "10px 12px", color: C.muted, textAlign: "center" }}>{i + 1}</td>
                  <td style={{ padding: "10px 12px" }}>
                    <div style={{ color: C.text, fontWeight: 600 }}>{t.name}</div>
                    <div style={{ color: C.muted, fontSize: 11 }}>{t.abbreviation}</div>
                  </td>
                  <td style={{ padding: "10px 12px", textAlign: "center" }}>
                    <Badge color={t.conference === "East" ? C.accent : C.accent2}>{t.conference}</Badge>
                  </td>
                  <td style={{ padding: "10px 12px", textAlign: "center", color: C.success, fontWeight: 700 }}>{t.wins}</td>
                  <td style={{ padding: "10px 12px", textAlign: "center", color: C.danger }}>{t.losses}</td>
                  <td style={{ padding: "10px 12px", textAlign: "center", color: C.text }}>{((t.wins / (t.wins + t.losses)) * 100).toFixed(0)}%</td>
                  <td style={{ padding: "10px 12px", textAlign: "center", color: C.text }}>{t.offensive_rating}</td>
                  <td style={{ padding: "10px 12px", textAlign: "center", color: C.text }}>{t.defensive_rating}</td>
                  <td style={{ padding: "10px 12px", textAlign: "center", color: t.net_rating > 0 ? C.success : C.danger, fontWeight: 600 }}>
                    {t.net_rating > 0 ? "+" : ""}{t.net_rating}
                  </td>
                  <td style={{ padding: "10px 12px", textAlign: "center", color: C.muted }}>{t.pace}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

// ── TAB 2: Shot Analytics ─────────────────────────────────────────
const ShotAnalyticsTab = () => {
  const [shotData, setShotData] = useState([]);
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(true);
  const [predLoading, setPredLoading] = useState(false);
  const [form, setForm] = useState({
    shot_distance: 22, shot_angle: 0, shot_type: "Jump Shot",
    is_three_pointer: true, is_catch_and_shoot: false,
    defender_distance: 4, quarter: 2, time_remaining_seconds: 400,
    shot_clock: 14, is_home: true, dribbles_before_shot: 1, touch_time: 2,
  });

  useEffect(() => {
    api.getShotChartData(null, 800).then(d => {
      setShotData(d);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  const handlePredict = () => {
    setPredLoading(true);
    api.predictShotProbability(form).then(r => {
      setPrediction(r);
      setPredLoading(false);
    }).catch(() => setPredLoading(false));
  };

  const made = shotData.filter(s => s.made);
  const missed = shotData.filter(s => !s.made);
  const makeRate = shotData.length > 0 ? (made.length / shotData.length * 100).toFixed(1) : 0;

  return (
    <div>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 24, marginBottom: 24 }}>
        {/* Shot Chart */}
        <div style={{ background: C.card, border: `1px solid ${C.border}`, borderRadius: 12, padding: 24 }}>
          <SectionTitle sub={`${shotData.length} shots | ${makeRate}% FG`}>NBA Shot Chart</SectionTitle>
          {loading ? <Loader /> : (
            <svg viewBox="0 0 500 470" width="100%" style={{ borderRadius: 8 }}>
              <CourtBackground />
              {missed.slice(0, 400).map((s, i) => (
                <circle key={`m${i}`} cx={courtX(s.x)} cy={courtY(s.y)}
                  r="3.5" fill={C.missed} opacity="0.45" />
              ))}
              {made.slice(0, 300).map((s, i) => (
                <circle key={`h${i}`} cx={courtX(s.x)} cy={courtY(s.y)}
                  r="4.5" fill={C.made} opacity="0.7" />
              ))}
            </svg>
          )}
          <div style={{ display: "flex", gap: 16, marginTop: 12, justifyContent: "center" }}>
            <div style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 12, color: C.muted }}>
              <div style={{ width: 10, height: 10, borderRadius: "50%", background: C.made }} />Made
            </div>
            <div style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 12, color: C.muted }}>
              <div style={{ width: 10, height: 10, borderRadius: "50%", background: C.missed }} />Missed
            </div>
          </div>
        </div>

        {/* Shot Probability Predictor */}
        <div style={{ background: C.card, border: `1px solid ${C.border}`, borderRadius: 12, padding: 24 }}>
          <SectionTitle sub="ML-powered shot probability">Shot Predictor</SectionTitle>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, marginBottom: 16 }}>
            {[
              { key: "shot_distance", label: "Distance (ft)", type: "number", min: 0, max: 35 },
              { key: "shot_angle",    label: "Angle (°)",     type: "number", min: -90, max: 90 },
              { key: "defender_distance", label: "Defender Dist (ft)", type: "number", min: 0, max: 20 },
              { key: "shot_clock",    label: "Shot Clock (s)", type: "number", min: 1, max: 24 },
            ].map(f => (
              <div key={f.key}>
                <label style={{ color: C.muted, fontSize: 11, display: "block", marginBottom: 4 }}>{f.label}</label>
                <input type={f.type} value={form[f.key]}
                  onChange={e => setForm({ ...form, [f.key]: parseFloat(e.target.value) })}
                  min={f.min} max={f.max} step="0.5"
                  style={{
                    width: "100%", background: C.surface, border: `1px solid ${C.border}`,
                    color: C.text, borderRadius: 6, padding: "6px 10px", fontSize: 13,
                    boxSizing: "border-box",
                  }} />
              </div>
            ))}

            <div>
              <label style={{ color: C.muted, fontSize: 11, display: "block", marginBottom: 4 }}>Shot Type</label>
              <select value={form.shot_type}
                onChange={e => setForm({ ...form, shot_type: e.target.value })}
                style={{ width: "100%", background: C.surface, border: `1px solid ${C.border}`, color: C.text, borderRadius: 6, padding: "6px 10px", fontSize: 13 }}>
                {["Jump Shot", "Pull-Up Jump Shot", "Layup", "Dunk", "Floater", "Step Back Jump Shot"].map(t => (
                  <option key={t}>{t}</option>
                ))}
              </select>
            </div>
            <div>
              <label style={{ color: C.muted, fontSize: 11, display: "block", marginBottom: 4 }}>Quarter</label>
              <select value={form.quarter}
                onChange={e => setForm({ ...form, quarter: parseInt(e.target.value) })}
                style={{ width: "100%", background: C.surface, border: `1px solid ${C.border}`, color: C.text, borderRadius: 6, padding: "6px 10px", fontSize: 13 }}>
                {[1, 2, 3, 4].map(q => <option key={q}>Q{q}</option>)}
              </select>
            </div>
          </div>

          <div style={{ display: "flex", gap: 12, marginBottom: 16 }}>
            {[
              { key: "is_three_pointer", label: "3-Pointer" },
              { key: "is_catch_and_shoot", label: "Catch & Shoot" },
              { key: "is_home", label: "Home Game" },
            ].map(f => (
              <label key={f.key} style={{ display: "flex", alignItems: "center", gap: 6, cursor: "pointer", color: C.muted, fontSize: 12 }}>
                <input type="checkbox" checked={form[f.key]}
                  onChange={e => setForm({ ...form, [f.key]: e.target.checked })} />
                {f.label}
              </label>
            ))}
          </div>

          <button onClick={handlePredict} disabled={predLoading}
            style={{
              background: C.accent, color: "#fff", border: "none", borderRadius: 8,
              padding: "10px 24px", fontSize: 14, fontWeight: 600, cursor: "pointer",
              width: "100%", opacity: predLoading ? 0.7 : 1,
            }}>
            {predLoading ? "Predicting..." : "🎯 Predict Shot Probability"}
          </button>

          {prediction && (
            <div style={{ marginTop: 20 }}>
              <div style={{
                background: C.surface, borderRadius: 12, padding: 20,
                border: `2px solid ${prediction.probability > 0.5 ? C.success : prediction.probability > 0.4 ? C.warning : C.danger}`,
                textAlign: "center",
              }}>
                <div style={{ fontSize: 48, fontWeight: 800, color: prediction.probability > 0.5 ? C.success : prediction.probability > 0.4 ? C.warning : C.danger }}>
                  {prediction.made_probability_pct}%
                </div>
                <div style={{ color: C.muted, fontSize: 13, marginTop: 4 }}>Shot Make Probability</div>
                <div style={{ marginTop: 12, display: "flex", gap: 8, justifyContent: "center", flexWrap: "wrap" }}>
                  <Badge color={prediction.shot_quality === "Elite" ? C.success : prediction.shot_quality === "Good" ? C.accent : prediction.shot_quality === "Average" ? C.warning : C.danger}>
                    {prediction.shot_quality}
                  </Badge>
                  <Badge color={C.muted}>xVal: {prediction.expected_value} pts</Badge>
                  <Badge color={C.muted}>Model: {prediction.model_used}</Badge>
                </div>
              </div>
              {prediction.feature_importance && (
                <div style={{ marginTop: 16 }}>
                  <div style={{ color: C.muted, fontSize: 12, marginBottom: 8 }}>Top Feature Importances</div>
                  {Object.entries(prediction.feature_importance).slice(0, 5).map(([f, v]) => (
                    <div key={f} style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 6 }}>
                      <div style={{ color: C.muted, fontSize: 11, width: 160 }}>{f.replace(/_/g, " ")}</div>
                      <div style={{ flex: 1, background: C.border, borderRadius: 4, height: 6 }}>
                        <div style={{ width: `${v * 100}%`, background: C.accent, borderRadius: 4, height: "100%", maxWidth: "100%" }} />
                      </div>
                      <div style={{ color: C.text, fontSize: 11, width: 40 }}>{(v * 100).toFixed(1)}%</div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// ── TAB 3: Player Explorer ────────────────────────────────────────
const PlayerExplorerTab = () => {
  const [players, setPlayers] = useState([]);
  const [selected, setSelected] = useState(null);
  const [radar, setRadar] = useState(null);
  const [zones, setZones] = useState(null);
  const [perf, setPerf] = useState(null);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getPlayers({ page_size: 40, sort_by: "points_per_game" })
      .then(d => { setPlayers(d.items || []); setLoading(false); })
      .catch(() => setLoading(false));
  }, []);

  const handleSelect = async (player) => {
    setSelected(player);
    setRadar(null); setZones(null); setPerf(null);
    const [r, z] = await Promise.all([
      api.getPlayerRadar(player.id),
      api.getPlayerShotZones(player.id),
    ]);
    setRadar(r);
    setZones(z);
    api.predictPlayerPerformance({ player_id: player.id, is_home: true, rest_days: 1, projected_minutes: player.minutes_per_game })
      .then(setPerf).catch(() => {});
  };

  const filtered = players.filter(p => p.name.toLowerCase().includes(search.toLowerCase()));

  return (
    <div style={{ display: "grid", gridTemplateColumns: "280px 1fr", gap: 24 }}>
      {/* Player list */}
      <div style={{ background: C.card, border: `1px solid ${C.border}`, borderRadius: 12, padding: 16, height: "fit-content" }}>
        <input placeholder="Search player..." value={search}
          onChange={e => setSearch(e.target.value)}
          style={{
            width: "100%", background: C.surface, border: `1px solid ${C.border}`,
            color: C.text, borderRadius: 8, padding: "8px 12px", fontSize: 13,
            marginBottom: 12, boxSizing: "border-box",
          }} />
        {loading ? <Loader /> : (
          <div style={{ maxHeight: 600, overflowY: "auto" }}>
            {filtered.map(p => (
              <div key={p.id} onClick={() => handleSelect(p)}
                style={{
                  padding: "10px 12px", borderRadius: 8, cursor: "pointer", marginBottom: 4,
                  background: selected?.id === p.id ? C.accent + "22" : "transparent",
                  border: `1px solid ${selected?.id === p.id ? C.accent : "transparent"}`,
                  transition: "all 0.15s",
                }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <div>
                    <div style={{ color: C.text, fontSize: 13, fontWeight: 600 }}>{p.name}</div>
                    <div style={{ color: C.muted, fontSize: 11 }}>{p.team_name || "FA"} · {p.position}</div>
                  </div>
                  <div style={{ color: C.accent, fontWeight: 700, fontSize: 14 }}>{p.points_per_game}</div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Player detail */}
      {selected ? (
        <div>
          {/* Header */}
          <div style={{ background: C.card, border: `1px solid ${C.border}`, borderRadius: 12, padding: 24, marginBottom: 20 }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
              <div>
                <h2 style={{ color: C.text, margin: 0, fontSize: 24, fontWeight: 800 }}>{selected.name}</h2>
                <div style={{ color: C.muted, marginTop: 4 }}>{selected.team_name} · {selected.position} · #{selected.jersey_number}</div>
              </div>
              <div style={{ display: "flex", gap: 8 }}>
                <Badge color={C.accent}>{selected.position}</Badge>
                <Badge color={C.success}>{selected.player_efficiency_rating} PER</Badge>
              </div>
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(6, 1fr)", gap: 16, marginTop: 20 }}>
              {[
                { label: "PPG", value: selected.points_per_game, color: C.accent },
                { label: "APG", value: selected.assists_per_game, color: C.accent2 },
                { label: "RPG", value: selected.rebounds_per_game, color: C.success },
                { label: "FG%", value: (selected.field_goal_pct * 100).toFixed(1) + "%", color: C.warning },
                { label: "3P%", value: (selected.three_point_pct * 100).toFixed(1) + "%", color: C.accent },
                { label: "TS%", value: (selected.true_shooting_pct * 100).toFixed(1) + "%", color: C.success },
              ].map(s => (
                <div key={s.label} style={{ textAlign: "center" }}>
                  <div style={{ color: s.color, fontSize: 22, fontWeight: 800 }}>{s.value}</div>
                  <div style={{ color: C.muted, fontSize: 11 }}>{s.label}</div>
                </div>
              ))}
            </div>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20 }}>
            {/* Radar chart */}
            {radar && (
              <div style={{ background: C.card, border: `1px solid ${C.border}`, borderRadius: 12, padding: 24 }}>
                <SectionTitle sub="Normalized skill ratings">Skill Radar</SectionTitle>
                <ResponsiveContainer width="100%" height={260}>
                  <RadarChart data={radar.stats} margin={{ top: 0, right: 20, bottom: 0, left: 20 }}>
                    <PolarGrid stroke={C.border} />
                    <PolarAngleAxis dataKey="stat" tick={{ fill: C.muted, fontSize: 12 }} />
                    <PolarRadiusAxis angle={30} domain={[0, 100]} tick={{ fill: C.muted, fontSize: 9 }} />
                    <Radar dataKey="value" stroke={C.accent} fill={C.accent} fillOpacity={0.3} strokeWidth={2} />
                  </RadarChart>
                </ResponsiveContainer>
              </div>
            )}

            {/* Shot zones */}
            {zones && zones.zones && (
              <div style={{ background: C.card, border: `1px solid ${C.border}`, borderRadius: 12, padding: 24 }}>
                <SectionTitle sub="FG% by court zone">Shot Zone Breakdown</SectionTitle>
                <ResponsiveContainer width="100%" height={260}>
                  <BarChart data={zones.zones} margin={{ top: 0, right: 10, left: -20, bottom: 50 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke={C.border} />
                    <XAxis dataKey="zone" stroke={C.muted} tick={{ fill: C.muted, fontSize: 9 }} angle={-35} textAnchor="end" />
                    <YAxis stroke={C.muted} tick={{ fill: C.muted, fontSize: 11 }} tickFormatter={v => (v * 100).toFixed(0) + "%"} />
                    <Tooltip
                      contentStyle={{ background: C.surface, border: `1px solid ${C.border}`, borderRadius: 8 }}
                      formatter={(v, n) => n === "fg_pct" ? [(v * 100).toFixed(1) + "%", "FG%"] : [v, n]} />
                    <Bar dataKey="fg_pct" name="FG%" fill={C.accent2} radius={[4, 4, 0, 0]} />
                    <Bar dataKey="attempts" name="Attempts" fill={C.border} radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}
          </div>

          {/* Performance prediction */}
          {perf && (
            <div style={{ background: C.card, border: `1px solid ${C.border}`, borderRadius: 12, padding: 24, marginTop: 20 }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
                <SectionTitle sub="AI-powered next game estimate">Performance Prediction</SectionTitle>
                <Badge color={perf.matchup_difficulty === "Tough" ? C.danger : perf.matchup_difficulty === "Easy" ? C.success : C.warning}>
                  {perf.matchup_difficulty} Matchup
                </Badge>
              </div>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(5, 1fr)", gap: 16 }}>
                {[
                  { label: "Predicted PTS", value: perf.predicted_points, color: C.accent },
                  { label: "Predicted AST", value: perf.predicted_assists, color: C.accent2 },
                  { label: "Predicted REB", value: perf.predicted_rebounds, color: C.success },
                  { label: "Predicted 3PM", value: perf.predicted_threes, color: C.warning },
                  { label: "Pred. PER",     value: perf.predicted_efficiency, color: C.danger },
                ].map(s => (
                  <div key={s.label} style={{ textAlign: "center", background: C.surface, borderRadius: 10, padding: 16, border: `1px solid ${C.border}` }}>
                    <div style={{ color: s.color, fontSize: 24, fontWeight: 800 }}>{s.value}</div>
                    <div style={{ color: C.muted, fontSize: 11, marginTop: 4 }}>{s.label}</div>
                  </div>
                ))}
              </div>
              <div style={{ color: C.muted, fontSize: 11, marginTop: 12 }}>
                95% CI: {perf.confidence_interval.lower} — {perf.confidence_interval.upper} pts
              </div>
            </div>
          )}
        </div>
      ) : (
        <div style={{ display: "flex", alignItems: "center", justifyContent: "center", color: C.muted, fontSize: 14 }}>
          ← Select a player to view analytics
        </div>
      )}
    </div>
  );
};

// ── TAB 4: Similarity Engine ──────────────────────────────────────
const SimilarityTab = () => {
  const [players, setPlayers] = useState([]);
  const [selectedId, setSelectedId] = useState("");
  const [result, setResult] = useState(null);
  const [clusterData, setClusterData] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    api.getPlayers({ page_size: 40, sort_by: "points_per_game" })
      .then(d => setPlayers(d.items || []));
    api.getClusterData().then(d => setClusterData(d.players || [])).catch(() => {});
  }, []);

  const handleFind = () => {
    if (!selectedId) return;
    setLoading(true);
    api.getPlayerSimilarity({ player_id: parseInt(selectedId), top_n: 6 })
      .then(r => { setResult(r); setLoading(false); })
      .catch(() => setLoading(false));
  };

  const CLUSTER_COLORS = [C.accent, C.accent2, C.success, C.warning, C.danger, "#ec4899"];

  return (
    <div>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 24, marginBottom: 24 }}>
        {/* Finder */}
        <div style={{ background: C.card, border: `1px solid ${C.border}`, borderRadius: 12, padding: 24 }}>
          <SectionTitle sub="K-Means clustering + Cosine similarity">Player Similarity Finder</SectionTitle>
          <select value={selectedId} onChange={e => setSelectedId(e.target.value)}
            style={{
              width: "100%", background: C.surface, border: `1px solid ${C.border}`,
              color: C.text, borderRadius: 8, padding: "10px 14px", fontSize: 14,
              marginBottom: 16,
            }}>
            <option value="">Select a player...</option>
            {players.map(p => (
              <option key={p.id} value={p.id}>{p.name} ({p.position} · {p.team_name})</option>
            ))}
          </select>
          <button onClick={handleFind} disabled={!selectedId || loading}
            style={{
              background: C.accent2, color: "#fff", border: "none", borderRadius: 8,
              padding: "10px 24px", fontSize: 14, fontWeight: 600, cursor: "pointer",
              width: "100%", opacity: !selectedId || loading ? 0.6 : 1,
            }}>
            {loading ? "Finding similar players..." : "🔍 Find Similar Players"}
          </button>

          {result && (
            <div style={{ marginTop: 24 }}>
              <div style={{ color: C.muted, fontSize: 12, marginBottom: 12 }}>
                Similar to <strong style={{ color: C.text }}>{result.target_player}</strong> — Cluster #{result.cluster}
              </div>
              {result.similar_players.map((p, i) => (
                <div key={p.player_id} style={{
                  background: C.surface, borderRadius: 10, padding: 14, marginBottom: 10,
                  border: `1px solid ${C.border}`, borderLeft: `3px solid ${CLUSTER_COLORS[p.cluster % 6]}`,
                }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                    <div>
                      <div style={{ color: C.text, fontWeight: 600, fontSize: 14 }}>{p.player_name}</div>
                      <div style={{ color: C.muted, fontSize: 11 }}>{p.team_name} · {p.position}</div>
                    </div>
                    <div style={{ textAlign: "right" }}>
                      <div style={{ color: C.success, fontWeight: 700, fontSize: 16 }}>
                        {(p.similarity_score * 100).toFixed(1)}%
                      </div>
                      <div style={{ color: C.muted, fontSize: 10 }}>similarity</div>
                    </div>
                  </div>
                  <div style={{ display: "flex", gap: 16, marginTop: 8 }}>
                    {[
                      { l: "PPG", v: p.points_per_game },
                      { l: "APG", v: p.assists_per_game },
                      { l: "RPG", v: p.rebounds_per_game },
                      { l: "PER", v: p.player_efficiency_rating },
                    ].map(s => (
                      <div key={s.l} style={{ textAlign: "center" }}>
                        <div style={{ color: C.accent, fontWeight: 700, fontSize: 13 }}>{s.v}</div>
                        <div style={{ color: C.muted, fontSize: 10 }}>{s.l}</div>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* PCA scatter */}
        <div style={{ background: C.card, border: `1px solid ${C.border}`, borderRadius: 12, padding: 24 }}>
          <SectionTitle sub="2D PCA projection of player feature vectors">Player Cluster Map</SectionTitle>
          {clusterData.length > 0 ? (
            <>
              <ResponsiveContainer width="100%" height={380}>
                <ScatterChart margin={{ top: 10, right: 10, bottom: 10, left: 10 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke={C.border} />
                  <XAxis type="number" dataKey="x" name="PC1" stroke={C.muted} tick={{ fill: C.muted, fontSize: 10 }} />
                  <YAxis type="number" dataKey="y" name="PC2" stroke={C.muted} tick={{ fill: C.muted, fontSize: 10 }} />
                  <Tooltip
                    contentStyle={{ background: C.surface, border: `1px solid ${C.border}`, borderRadius: 8, fontSize: 12 }}
                    content={({ payload }) => {
                      if (!payload?.length) return null;
                      const d = payload[0].payload;
                      return (
                        <div style={{ background: C.surface, border: `1px solid ${C.border}`, borderRadius: 8, padding: 10, fontSize: 12 }}>
                          <div style={{ color: C.text, fontWeight: 600 }}>{d.name}</div>
                          <div style={{ color: C.muted }}>{d.position} · {d.cluster_label}</div>
                          <div style={{ color: C.accent }}>{d.ppg} PPG</div>
                        </div>
                      );
                    }} />
                  {[0, 1, 2, 3, 4, 5].map(cluster => (
                    <Scatter key={cluster}
                      name={`Cluster ${cluster}`}
                      data={clusterData.filter(d => d.cluster === cluster)}
                      fill={CLUSTER_COLORS[cluster]} opacity={0.8} />
                  ))}
                </ScatterChart>
              </ResponsiveContainer>
              <div style={{ display: "flex", flexWrap: "wrap", gap: 8, marginTop: 8 }}>
                {[0, 1, 2, 3, 4, 5].map(c => (
                  <div key={c} style={{ display: "flex", alignItems: "center", gap: 5, fontSize: 11, color: C.muted }}>
                    <div style={{ width: 8, height: 8, borderRadius: "50%", background: CLUSTER_COLORS[c] }} />
                    {["Scoring Guard", "Playmaking Big", "3-and-D Wing", "Point Guard", "Interior", "Versatile FW"][c]}
                  </div>
                ))}
              </div>
            </>
          ) : (
            <div style={{ color: C.muted, textAlign: "center", padding: 40 }}>
              Train models first to see cluster visualization
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// ── TAB 5: Model Performance ──────────────────────────────────────
const ModelPerformanceTab = () => {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getModelMetrics().then(setMetrics).catch(() => {}).finally(() => setLoading(false));
  }, []);

  if (loading) return <Loader />;
  if (!metrics) return (
    <div style={{ textAlign: "center", padding: 60, color: C.muted }}>
      <div style={{ fontSize: 48, marginBottom: 16 }}>🤖</div>
      <div style={{ fontSize: 18, color: C.text, marginBottom: 8 }}>Models Not Trained Yet</div>
      <div>Run: <code style={{ background: C.card, padding: "2px 8px", borderRadius: 4, color: C.accent }}>
        docker compose up
      </code> to train all models automatically.</div>
    </div>
  );

  const modelData = metrics.shot_probability_models.map(m => ({
    name: m.model_name.replace(" ", "\n"),
    Accuracy: +(m.accuracy * 100).toFixed(1),
    "ROC-AUC": +(m.roc_auc * 100).toFixed(1),
    F1: +(m.f1_score * 100).toFixed(1),
    Precision: +(m.precision * 100).toFixed(1),
    Recall: +(m.recall * 100).toFixed(1),
  }));

  const fiData = Object.entries(metrics.feature_importance || {})
    .slice(0, 10)
    .map(([f, v]) => ({ feature: f.replace(/_/g, " "), importance: +(v * 100).toFixed(2) }));

  return (
    <div>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 16, marginBottom: 24 }}>
        <StatCard label="Best Model" value={metrics.best_model.replace("_", " ").toUpperCase()} sub="Highest ROC-AUC" icon="🏆" color={C.success} />
        <StatCard label="Training Date" value={metrics.training_date} sub="Last trained" icon="📅" color={C.accent} />
        <StatCard label="Models Compared" value={metrics.shot_probability_models.length} sub="LR · RF · XGBoost" icon="🧪" color={C.accent2} />
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 24, marginBottom: 24 }}>
        {/* Model comparison bar chart */}
        <div style={{ background: C.card, border: `1px solid ${C.border}`, borderRadius: 12, padding: 24 }}>
          <SectionTitle sub="Shot make probability classification">Model Comparison</SectionTitle>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={modelData} margin={{ top: 0, right: 10, left: -10, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke={C.border} />
              <XAxis dataKey="name" stroke={C.muted} tick={{ fill: C.muted, fontSize: 11 }} />
              <YAxis stroke={C.muted} tick={{ fill: C.muted, fontSize: 11 }} domain={[60, 80]} tickFormatter={v => v + "%"} />
              <Tooltip contentStyle={{ background: C.surface, border: `1px solid ${C.border}`, borderRadius: 8 }}
                formatter={v => v + "%"} />
              <Legend wrapperStyle={{ color: C.muted, fontSize: 12 }} />
              <Bar dataKey="Accuracy"  fill={C.accent}  radius={[3, 3, 0, 0]} />
              <Bar dataKey="ROC-AUC"  fill={C.success} radius={[3, 3, 0, 0]} />
              <Bar dataKey="F1"       fill={C.accent2} radius={[3, 3, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Feature importance */}
        <div style={{ background: C.card, border: `1px solid ${C.border}`, borderRadius: 12, padding: 24 }}>
          <SectionTitle sub="XGBoost feature importances">What Predicts Shots?</SectionTitle>
          {fiData.map((f, i) => (
            <div key={f.feature} style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 10 }}>
              <div style={{ color: C.muted, width: 180, fontSize: 12 }}>{f.feature}</div>
              <div style={{ flex: 1, background: C.border, borderRadius: 4, height: 8 }}>
                <div style={{
                  width: `${(f.importance / fiData[0].importance) * 100}%`,
                  background: `hsl(${220 - i * 18}, 70%, 60%)`,
                  borderRadius: 4, height: "100%",
                }} />
              </div>
              <div style={{ color: C.text, fontSize: 11, width: 45, textAlign: "right" }}>{f.importance}%</div>
            </div>
          ))}
        </div>
      </div>

      {/* Detailed metrics table */}
      <div style={{ background: C.card, border: `1px solid ${C.border}`, borderRadius: 12, padding: 24 }}>
        <SectionTitle sub="Full classification metrics for each model">Detailed Metrics</SectionTitle>
        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 14 }}>
          <thead>
            <tr style={{ color: C.muted, fontSize: 12, textTransform: "uppercase" }}>
              {["Model", "Accuracy", "ROC-AUC", "Precision", "Recall", "F1 Score", "Status"].map(h => (
                <th key={h} style={{ padding: "8px 16px", textAlign: h === "Model" ? "left" : "center", fontWeight: 500 }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {metrics.shot_probability_models.map(m => (
              <tr key={m.model_name} style={{ borderTop: `1px solid ${C.border}` }}>
                <td style={{ padding: "12px 16px", color: C.text, fontWeight: 600 }}>{m.model_name}</td>
                {[m.accuracy, m.roc_auc, m.precision, m.recall, m.f1_score].map((v, i) => (
                  <td key={i} style={{ padding: "12px 16px", textAlign: "center", color: v > 0.65 ? C.success : C.warning, fontWeight: 600 }}>
                    {(v * 100).toFixed(1)}%
                  </td>
                ))}
                <td style={{ padding: "12px 16px", textAlign: "center" }}>
                  {m.model_name === metrics.best_model.replace(/_/g, " ") || m.model_name.toLowerCase().includes(metrics.best_model.replace(/_/g, " ")) ? (
                    <Badge color={C.success}>Best</Badge>
                  ) : (
                    <Badge color={C.muted}>Trained</Badge>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

// ── Main App ──────────────────────────────────────────────────────
export default function App() {
  const [activeTab, setActiveTab] = useState(0);

  const TAB_COMPONENTS = [
    DashboardTab,
    ShotAnalyticsTab,
    PlayerExplorerTab,
    SimilarityTab,
    ModelPerformanceTab,
  ];

  const ActiveComponent = TAB_COMPONENTS[activeTab];

  return (
    <div style={{ minHeight: "100vh", background: C.bg, color: C.text, fontFamily: "'Inter', system-ui, sans-serif" }}>
      {/* Header */}
      <header style={{
        background: C.surface, borderBottom: `1px solid ${C.border}`,
        padding: "0 32px", position: "sticky", top: 0, zIndex: 100,
      }}>
        <div style={{ maxWidth: 1400, margin: "0 auto", display: "flex", alignItems: "center", height: 64 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10, marginRight: 48 }}>
            <div style={{ fontSize: 28 }}>🏀</div>
            <div>
              <div style={{ color: C.text, fontWeight: 800, fontSize: 18, letterSpacing: "-0.5px" }}>HoopMind AI</div>
              <div style={{ color: C.muted, fontSize: 10, letterSpacing: 2, textTransform: "uppercase" }}>NBA Analytics Platform</div>
            </div>
          </div>
          <nav style={{ display: "flex", gap: 4 }}>
            {TABS.map((tab, i) => (
              <button key={tab} onClick={() => setActiveTab(i)}
                style={{
                  background: activeTab === i ? C.accent + "22" : "transparent",
                  color: activeTab === i ? C.accent : C.muted,
                  border: `1px solid ${activeTab === i ? C.accent + "44" : "transparent"}`,
                  borderRadius: 8, padding: "6px 16px", fontSize: 13, fontWeight: 500,
                  cursor: "pointer", transition: "all 0.15s",
                }}>
                {tab}
              </button>
            ))}
          </nav>
          <div style={{ marginLeft: "auto", display: "flex", alignItems: "center", gap: 8 }}>
            <div style={{ width: 8, height: 8, borderRadius: "50%", background: C.success, boxShadow: `0 0 8px ${C.success}` }} />
            <span style={{ color: C.muted, fontSize: 12 }}>API Connected</span>
          </div>
        </div>
      </header>

      {/* Main content */}
      <main style={{ maxWidth: 1400, margin: "0 auto", padding: "28px 32px" }}>
        {/* Breadcrumb */}
        <div style={{ marginBottom: 24, display: "flex", alignItems: "center", gap: 8 }}>
          <span style={{ color: C.muted, fontSize: 13 }}>HoopMind AI</span>
          <span style={{ color: C.border }}>›</span>
          <span style={{ color: C.text, fontSize: 13, fontWeight: 600 }}>{TABS[activeTab]}</span>
        </div>

        <ActiveComponent />
      </main>

      {/* Footer */}
      <footer style={{ borderTop: `1px solid ${C.border}`, padding: "16px 32px", marginTop: 40 }}>
        <div style={{ maxWidth: 1400, margin: "0 auto", display: "flex", justifyContent: "space-between", color: C.muted, fontSize: 12 }}>
          <div>HoopMind AI · NBA Analytics Platform · ML-Powered</div>
          <div>FastAPI + XGBoost + React · 2023-24 Season</div>
        </div>
      </footer>
    </div>
  );
}
