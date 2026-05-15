import React, { useState, useEffect } from "react";
import {
  BarChart, Bar, LineChart, Line, RadarChart, Radar, PolarGrid,
  PolarAngleAxis, PolarRadiusAxis, ScatterChart, Scatter,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  ResponsiveContainer, Cell,
} from "recharts";
import * as api from "./services/api";
import "./App.css";

// ── Design Tokens ──────────────────────────────────────────────
const C = {
  bg:       "#000000",
  surface:  "#0d0d0d",
  card:     "#141414",
  card2:    "#1c1c1c",
  border:   "#2a2a2a",
  border2:  "#333333",
  accent:   "#F97316",   // orange
  accentDim:"#F9731620",
  accentBorder:"#F9731640",
  white:    "#FFFFFF",
  text:     "#F0F0F0",
  muted:    "#888888",
  muted2:   "#555555",
  success:  "#22C55E",
  danger:   "#EF4444",
  warning:  "#EAB308",
};

const TABS = [
  { id: 0, label: "Overview" },
  { id: 1, label: "Shot Analytics" },
  { id: 2, label: "Players" },
  { id: 3, label: "Similarity" },
  { id: 4, label: "Models" },
];

// ── SVG Icons ─────────────────────────────────────────────────
const Icon = ({ name, size = 16, color = C.muted }) => {
  const icons = {
    teams: (
      <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="1.5">
        <circle cx="9" cy="7" r="4"/><path d="M3 21v-2a4 4 0 0 1 4-4h4a4 4 0 0 1 4 4v2"/>
        <path d="M16 3.13a4 4 0 0 1 0 7.75"/><path d="M21 21v-2a4 4 0 0 0-3-3.85"/>
      </svg>
    ),
    player: (
      <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="1.5">
        <circle cx="12" cy="8" r="4"/><path d="M4 20v-2a8 8 0 0 1 16 0v2"/>
      </svg>
    ),
    shot: (
      <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="1.5">
        <circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="3"/>
        <line x1="12" y1="2" x2="12" y2="9"/><line x1="12" y1="15" x2="12" y2="22"/>
        <line x1="2" y1="12" x2="9" y2="12"/><line x1="15" y1="12" x2="22" y2="12"/>
      </svg>
    ),
    model: (
      <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="1.5">
        <path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/>
      </svg>
    ),
    chart: (
      <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="1.5">
        <line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/>
        <line x1="6" y1="20" x2="6" y2="14"/><line x1="2" y1="20" x2="22" y2="20"/>
      </svg>
    ),
    arrow: (
      <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="1.5">
        <line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/>
      </svg>
    ),
    check: (
      <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="2">
        <polyline points="20 6 9 17 4 12"/>
      </svg>
    ),
    dot: (
      <svg width={size} height={size} viewBox="0 0 24 24" fill={color}>
        <circle cx="12" cy="12" r="6"/>
      </svg>
    ),
    search: (
      <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="1.5">
        <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
      </svg>
    ),
    filter: (
      <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke={color} strokeWidth="1.5">
        <polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/>
      </svg>
    ),
    star: (
      <svg width={size} height={size} viewBox="0 0 24 24" fill={color} stroke="none">
        <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
      </svg>
    ),
  };
  return icons[name] || null;
};

// ── Core Components ───────────────────────────────────────────
const StatCard = ({ label, value, sub, accent = false, icon }) => (
  <div style={{
    background: C.card,
    border: `1px solid ${accent ? C.accentBorder : C.border}`,
    borderRadius: 8,
    padding: "20px 24px",
    borderTop: accent ? `2px solid ${C.accent}` : `1px solid ${C.border}`,
  }}>
    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
      <div>
        <div style={{ color: C.muted, fontSize: 11, fontWeight: 500, textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: 8 }}>
          {label}
        </div>
        <div style={{ color: accent ? C.accent : C.white, fontSize: 26, fontWeight: 700, lineHeight: 1 }}>
          {value}
        </div>
        {sub && <div style={{ color: C.muted2, fontSize: 11, marginTop: 6 }}>{sub}</div>}
      </div>
      {icon && <div style={{ opacity: 0.4 }}><Icon name={icon} size={20} color={accent ? C.accent : C.muted} /></div>}
    </div>
  </div>
);

const SectionHeader = ({ title, sub }) => (
  <div style={{ marginBottom: 20 }}>
    <h2 style={{ color: C.white, fontSize: 15, fontWeight: 600, margin: 0, letterSpacing: "-0.01em" }}>{title}</h2>
    {sub && <div style={{ color: C.muted, fontSize: 12, marginTop: 4 }}>{sub}</div>}
  </div>
);

const Pill = ({ children, color = C.muted, bg }) => (
  <span style={{
    background: bg || color + "18",
    color,
    border: `1px solid ${color}30`,
    borderRadius: 4,
    padding: "2px 8px",
    fontSize: 11,
    fontWeight: 600,
    letterSpacing: "0.02em",
  }}>{children}</span>
);

const Loader = () => (
  <div style={{ display: "flex", alignItems: "center", justifyContent: "center", padding: 60, color: C.muted2 }}>
    <div style={{ textAlign: "center" }}>
      <div style={{ width: 32, height: 32, border: `2px solid ${C.border2}`, borderTop: `2px solid ${C.accent}`, borderRadius: "50%", animation: "spin 0.8s linear infinite", margin: "0 auto 12px" }} />
      <div style={{ fontSize: 12 }}>Loading data</div>
    </div>
  </div>
);

const Divider = () => <div style={{ height: 1, background: C.border, margin: "0" }} />;

const inputStyle = {
  width: "100%",
  background: C.surface,
  border: `1px solid ${C.border}`,
  color: C.text,
  borderRadius: 6,
  padding: "8px 12px",
  fontSize: 13,
  boxSizing: "border-box",
  outline: "none",
};

const selectStyle = {
  ...inputStyle,
  cursor: "pointer",
};

const btnPrimary = {
  background: C.accent,
  color: "#000",
  border: "none",
  borderRadius: 6,
  padding: "9px 20px",
  fontSize: 13,
  fontWeight: 700,
  cursor: "pointer",
  width: "100%",
  letterSpacing: "0.02em",
};

// ── NBA Court SVG ─────────────────────────────────────────────
const CourtBg = () => (
  <g>
    <rect x="0" y="0" width="500" height="470" fill="#0d0d0d" rx="4"/>
    <rect x="170" y="290" width="160" height="145" fill="none" stroke="#222" strokeWidth="1.5"/>
    <ellipse cx="250" cy="290" rx="60" ry="60" fill="none" stroke="#222" strokeWidth="1.5"/>
    <circle cx="250" cy="420" r="7.5" fill="none" stroke={C.accent} strokeWidth="1.5" opacity="0.6"/>
    <line x1="220" y1="435" x2="280" y2="435" stroke="#222" strokeWidth="1.5"/>
    <path d="M 60 435 L 60 280 A 210 210 0 0 1 440 280 L 440 435" fill="none" stroke="#222" strokeWidth="1.5"/>
  </g>
);

const cX = (x) => 250 + x * 10;
const cY = (y) => 420 - (y - 5.25) * 10;

// ── TAB: Overview ─────────────────────────────────────────────
const OverviewTab = () => {
  const [players, setPlayers] = useState([]);
  const [teams, setTeams] = useState([]);
  const [leaderboard, setLeaderboard] = useState([]);
  const [shotSummary, setShotSummary] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeStat, setActiveStat] = useState("points_per_game");

  const STATS = [
    { key: "points_per_game", label: "PTS" },
    { key: "assists_per_game", label: "AST" },
    { key: "rebounds_per_game", label: "REB" },
    { key: "player_efficiency_rating", label: "PER" },
    { key: "true_shooting_pct", label: "TS%" },
    { key: "win_shares", label: "WS" },
  ];

  useEffect(() => {
    Promise.all([
      api.getPlayers({ page_size: 5 }),
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

  return (
    <div>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 12, marginBottom: 24 }}>
        <StatCard label="Franchises" value="30" sub="2023–24 Season" icon="teams" accent />
        <StatCard label="Players" value="40+" sub="Active roster" icon="player" />
        <StatCard label="Shot records" value="60K+" sub="Season logs" icon="shot" />
        <StatCard label="ML Models" value="3" sub="LR · RF · XGBoost" icon="model" />
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1.4fr", gap: 16, marginBottom: 16 }}>
        {/* Leaderboard */}
        <div style={{ background: C.card, border: `1px solid ${C.border}`, borderRadius: 8, overflow: "hidden" }}>
          <div style={{ padding: "16px 20px", borderBottom: `1px solid ${C.border}` }}>
            <div style={{ color: C.white, fontWeight: 600, fontSize: 13, marginBottom: 12 }}>League Leaderboard</div>
            <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
              {STATS.map(s => (
                <button key={s.key} onClick={() => setActiveStat(s.key)} style={{
                  background: activeStat === s.key ? C.accent : "transparent",
                  color: activeStat === s.key ? "#000" : C.muted,
                  border: `1px solid ${activeStat === s.key ? C.accent : C.border}`,
                  borderRadius: 4, padding: "3px 10px", fontSize: 11, cursor: "pointer",
                  fontWeight: activeStat === s.key ? 700 : 400,
                }}>{s.label}</button>
              ))}
            </div>
          </div>
          <div>
            {leaderboard.map((p, i) => (
              <div key={p.player_id} style={{
                display: "flex", alignItems: "center", padding: "10px 20px",
                borderBottom: i < leaderboard.length - 1 ? `1px solid ${C.border}` : "none",
                background: i === 0 ? C.accentDim : "transparent",
              }}>
                <div style={{ color: i === 0 ? C.accent : C.muted2, width: 20, fontSize: 11, fontWeight: 700 }}>
                  {i + 1}
                </div>
                <div style={{ flex: 1, marginLeft: 12 }}>
                  <div style={{ color: C.text, fontSize: 13, fontWeight: 500 }}>{p.player_name}</div>
                  <div style={{ color: C.muted2, fontSize: 11 }}>{p.team} · {p.position}</div>
                </div>
                <div style={{ color: i === 0 ? C.accent : C.white, fontWeight: 700, fontSize: 15 }}>
                  {typeof p.value === "number" && p.value < 1 ? (p.value * 100).toFixed(1) + "%" : p.value}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Shot zones */}
        <div style={{ background: C.card, border: `1px solid ${C.border}`, borderRadius: 8, padding: 20 }}>
          <SectionHeader title="Shot Distribution by Zone" sub="League-wide FG% across court regions" />
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={shotSummary} margin={{ top: 0, right: 0, left: -24, bottom: 55 }}>
              <CartesianGrid strokeDasharray="3 3" stroke={C.border} vertical={false} />
              <XAxis dataKey="zone" stroke="none" tick={{ fill: C.muted, fontSize: 10 }} angle={-35} textAnchor="end" />
              <YAxis stroke="none" tick={{ fill: C.muted, fontSize: 10 }} tickFormatter={v => (v * 100).toFixed(0) + "%"} />
              <Tooltip
                contentStyle={{ background: C.card2, border: `1px solid ${C.border}`, borderRadius: 6, fontSize: 12 }}
                labelStyle={{ color: C.white, fontWeight: 600 }}
                formatter={(v, n) => n === "fg_pct" ? [(v * 100).toFixed(1) + "%", "FG%"] : [v.toLocaleString(), n]}
              />
              <Bar dataKey="fg_pct" name="FG%" radius={[3, 3, 0, 0]}>
                {shotSummary.map((_, i) => (
                  <Cell key={i} fill={i === 0 ? C.accent : `hsl(${20 + i * 25}, 70%, 50%)`} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Teams table */}
      <div style={{ background: C.card, border: `1px solid ${C.border}`, borderRadius: 8, overflow: "hidden" }}>
        <div style={{ padding: "16px 20px", borderBottom: `1px solid ${C.border}` }}>
          <SectionHeader title="Team Standings" sub="2023–24 · sorted by wins" />
        </div>
        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 12 }}>
            <thead>
              <tr style={{ background: C.surface }}>
                {["#", "Team", "Conf", "W", "L", "Win%", "OFF RTG", "DEF RTG", "NET RTG", "PACE"].map(h => (
                  <th key={h} style={{
                    padding: "10px 16px", textAlign: h === "Team" ? "left" : "center",
                    color: C.muted, fontWeight: 500, fontSize: 10, textTransform: "uppercase", letterSpacing: "0.05em",
                    borderBottom: `1px solid ${C.border}`,
                  }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {teams.slice(0, 15).map((t, i) => (
                <tr key={t.id} style={{ borderBottom: `1px solid ${C.border}`, background: i % 2 === 0 ? "transparent" : C.surface + "80" }}>
                  <td style={{ padding: "10px 16px", color: C.muted2, textAlign: "center", fontSize: 11 }}>{i + 1}</td>
                  <td style={{ padding: "10px 16px" }}>
                    <div style={{ color: C.text, fontWeight: 600, fontSize: 13 }}>{t.name}</div>
                    <div style={{ color: C.muted2, fontSize: 10, marginTop: 1 }}>{t.abbreviation}</div>
                  </td>
                  <td style={{ padding: "10px 16px", textAlign: "center" }}>
                    <Pill color={t.conference === "East" ? C.accent : "#A78BFA"}>{t.conference}</Pill>
                  </td>
                  <td style={{ padding: "10px 16px", textAlign: "center", color: C.success, fontWeight: 700 }}>{t.wins}</td>
                  <td style={{ padding: "10px 16px", textAlign: "center", color: C.muted }}>{t.losses}</td>
                  <td style={{ padding: "10px 16px", textAlign: "center", color: C.text }}>{((t.wins / (t.wins + t.losses)) * 100).toFixed(0)}%</td>
                  <td style={{ padding: "10px 16px", textAlign: "center", color: C.text }}>{t.offensive_rating}</td>
                  <td style={{ padding: "10px 16px", textAlign: "center", color: C.text }}>{t.defensive_rating}</td>
                  <td style={{ padding: "10px 16px", textAlign: "center", color: t.net_rating > 0 ? C.success : C.danger, fontWeight: 600 }}>
                    {t.net_rating > 0 ? "+" : ""}{t.net_rating}
                  </td>
                  <td style={{ padding: "10px 16px", textAlign: "center", color: C.muted }}>{t.pace}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

// ── TAB: Shot Analytics ───────────────────────────────────────
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
    api.getShotChartData(null, 800).then(d => { setShotData(d); setLoading(false); }).catch(() => setLoading(false));
  }, []);

  const handlePredict = () => {
    setPredLoading(true);
    const payload = { ...form, quarter: parseInt(form.quarter) };
    api.predictShotProbability(payload).then(r => { setPrediction(r); setPredLoading(false); }).catch(() => setPredLoading(false));
  };

  const made = shotData.filter(s => s.made);
  const missed = shotData.filter(s => !s.made);
  const makeRate = shotData.length > 0 ? (made.length / shotData.length * 100).toFixed(1) : 0;

  const qualityColor = (q) => ({ Elite: C.success, Good: C.accent, Average: C.warning, Poor: C.danger }[q] || C.muted);

  return (
    <div>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
        {/* Court */}
        <div style={{ background: C.card, border: `1px solid ${C.border}`, borderRadius: 8, padding: 20 }}>
          <SectionHeader title="Shot Chart" sub={`${shotData.length.toLocaleString()} attempts · ${makeRate}% FG`} />
          {loading ? <Loader /> : (
            <svg viewBox="0 0 500 470" width="100%" style={{ borderRadius: 6 }}>
              <CourtBg />
              {missed.slice(0, 400).map((s, i) => (
                <circle key={`m${i}`} cx={cX(s.x)} cy={cY(s.y)} r="3" fill={C.danger} opacity="0.35" />
              ))}
              {made.slice(0, 300).map((s, i) => (
                <circle key={`h${i}`} cx={cX(s.x)} cy={cY(s.y)} r="4" fill={C.success} opacity="0.65" />
              ))}
            </svg>
          )}
          <div style={{ display: "flex", gap: 20, marginTop: 12, justifyContent: "center" }}>
            {[{ color: C.success, label: "Made" }, { color: C.danger, label: "Missed" }].map(l => (
              <div key={l.label} style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 11, color: C.muted }}>
                <div style={{ width: 8, height: 8, borderRadius: "50%", background: l.color }} />{l.label}
              </div>
            ))}
          </div>
        </div>

        {/* Predictor */}
        <div style={{ background: C.card, border: `1px solid ${C.border}`, borderRadius: 8, padding: 20 }}>
          <SectionHeader title="Shot Probability" sub="ML-powered make probability estimator" />
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10, marginBottom: 14 }}>
            {[
              { key: "shot_distance", label: "Distance (ft)", min: 0, max: 35, step: 0.5 },
              { key: "shot_angle", label: "Angle (°)", min: -90, max: 90, step: 1 },
              { key: "defender_distance", label: "Defender (ft)", min: 0, max: 20, step: 0.5 },
              { key: "shot_clock", label: "Shot Clock (s)", min: 1, max: 24, step: 1 },
              { key: "dribbles_before_shot", label: "Dribbles", min: 0, max: 10, step: 1 },
              { key: "touch_time", label: "Touch Time (s)", min: 0, max: 10, step: 0.5 },
            ].map(f => (
              <div key={f.key}>
                <label style={{ color: C.muted, fontSize: 10, display: "block", marginBottom: 4, textTransform: "uppercase", letterSpacing: "0.05em" }}>{f.label}</label>
                <input type="number" value={form[f.key]}
                  onChange={e => setForm({ ...form, [f.key]: parseFloat(e.target.value) || 0 })}
                  min={f.min} max={f.max} step={f.step}
                  style={inputStyle} />
              </div>
            ))}
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10, marginBottom: 14 }}>
            <div>
              <label style={{ color: C.muted, fontSize: 10, display: "block", marginBottom: 4, textTransform: "uppercase", letterSpacing: "0.05em" }}>Shot Type</label>
              <select value={form.shot_type} onChange={e => setForm({ ...form, shot_type: e.target.value })} style={selectStyle}>
                {["Jump Shot", "Pull-Up Jump Shot", "Layup", "Dunk", "Floater", "Step Back Jump Shot"].map(t => <option key={t}>{t}</option>)}
              </select>
            </div>
            <div>
              <label style={{ color: C.muted, fontSize: 10, display: "block", marginBottom: 4, textTransform: "uppercase", letterSpacing: "0.05em" }}>Quarter</label>
              <select value={form.quarter} onChange={e => setForm({ ...form, quarter: parseInt(e.target.value) })} style={selectStyle}>
                {[1, 2, 3, 4].map(q => <option key={q} value={q}>Q{q}</option>)}
              </select>
            </div>
          </div>

          <div style={{ display: "flex", gap: 16, marginBottom: 16 }}>
            {[
              { key: "is_three_pointer", label: "3-Pointer" },
              { key: "is_catch_and_shoot", label: "Catch & Shoot" },
              { key: "is_home", label: "Home Game" },
            ].map(f => (
              <label key={f.key} style={{ display: "flex", alignItems: "center", gap: 6, cursor: "pointer", color: C.muted, fontSize: 12 }}>
                <input type="checkbox" checked={form[f.key]} onChange={e => setForm({ ...form, [f.key]: e.target.checked })}
                  style={{ accentColor: C.accent }} />
                {f.label}
              </label>
            ))}
          </div>

          <button onClick={handlePredict} disabled={predLoading} style={{ ...btnPrimary, opacity: predLoading ? 0.7 : 1 }}>
            {predLoading ? "Computing..." : "Run Prediction"}
          </button>

          {prediction && (
            <div style={{ marginTop: 16 }}>
              <div style={{
                background: C.surface, borderRadius: 8, padding: 20,
                border: `1px solid ${qualityColor(prediction.shot_quality)}40`,
                borderTop: `2px solid ${qualityColor(prediction.shot_quality)}`,
                textAlign: "center",
              }}>
                <div style={{ fontSize: 52, fontWeight: 800, color: qualityColor(prediction.shot_quality), lineHeight: 1 }}>
                  {prediction.made_probability_pct}%
                </div>
                <div style={{ color: C.muted, fontSize: 11, marginTop: 6, textTransform: "uppercase", letterSpacing: "0.08em" }}>
                  Make Probability
                </div>
                <div style={{ display: "flex", gap: 8, justifyContent: "center", marginTop: 12, flexWrap: "wrap" }}>
                  <Pill color={qualityColor(prediction.shot_quality)}>{prediction.shot_quality}</Pill>
                  <Pill color={C.muted}>xVal {prediction.expected_value} pts</Pill>
                  <Pill color={C.muted}>{prediction.model_used}</Pill>
                </div>
              </div>

              {prediction.feature_importance && (
                <div style={{ marginTop: 14 }}>
                  <div style={{ color: C.muted, fontSize: 10, textTransform: "uppercase", letterSpacing: "0.05em", marginBottom: 10 }}>Feature Importances</div>
                  {Object.entries(prediction.feature_importance).slice(0, 6).map(([f, v]) => (
                    <div key={f} style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 7 }}>
                      <div style={{ color: C.muted, fontSize: 10, width: 155 }}>{f.replace(/_/g, " ")}</div>
                      <div style={{ flex: 1, background: C.border, borderRadius: 2, height: 4 }}>
                        <div style={{ width: `${Math.min(v * 100, 100)}%`, background: C.accent, borderRadius: 2, height: "100%" }} />
                      </div>
                      <div style={{ color: C.muted, fontSize: 10, width: 36, textAlign: "right" }}>{(v * 100).toFixed(1)}%</div>
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

// ── TAB: Players ──────────────────────────────────────────────
const PlayersTab = () => {
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
    setSelected(player); setRadar(null); setZones(null); setPerf(null);
    const [r, z] = await Promise.all([api.getPlayerRadar(player.id), api.getPlayerShotZones(player.id)]);
    setRadar(r); setZones(z);
    api.predictPlayerPerformance({ player_id: player.id, is_home: true, rest_days: 1, projected_minutes: player.minutes_per_game })
      .then(setPerf).catch(() => {});
  };

  const filtered = players.filter(p => p.name.toLowerCase().includes(search.toLowerCase()));

  return (
    <div style={{ display: "grid", gridTemplateColumns: "260px 1fr", gap: 16 }}>
      <div style={{ background: C.card, border: `1px solid ${C.border}`, borderRadius: 8, overflow: "hidden" }}>
        <div style={{ padding: 14, borderBottom: `1px solid ${C.border}`, position: "relative" }}>
          <div style={{ position: "absolute", left: 26, top: "50%", transform: "translateY(-50%)", pointerEvents: "none" }}>
            <Icon name="search" size={14} color={C.muted2} />
          </div>
          <input placeholder="Search player..." value={search} onChange={e => setSearch(e.target.value)}
            style={{ ...inputStyle, paddingLeft: 32 }} />
        </div>
        {loading ? <Loader /> : (
          <div style={{ maxHeight: 620, overflowY: "auto" }}>
            {filtered.map(p => (
              <div key={p.id} onClick={() => handleSelect(p)} style={{
                padding: "10px 16px",
                background: selected?.id === p.id ? C.accentDim : "transparent",
                borderBottom: `1px solid ${C.border}`,
                borderLeft: `2px solid ${selected?.id === p.id ? C.accent : "transparent"}`,
                cursor: "pointer",
                transition: "all 0.1s",
              }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <div>
                    <div style={{ color: selected?.id === p.id ? C.white : C.text, fontSize: 13, fontWeight: 500 }}>{p.name}</div>
                    <div style={{ color: C.muted2, fontSize: 10, marginTop: 2 }}>{p.team_name || "Free Agent"} · {p.position}</div>
                  </div>
                  <div style={{ color: selected?.id === p.id ? C.accent : C.muted, fontWeight: 700, fontSize: 14 }}>
                    {p.points_per_game}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {selected ? (
        <div>
          <div style={{ background: C.card, border: `1px solid ${C.border}`, borderRadius: 8, padding: 20, marginBottom: 16 }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 20 }}>
              <div>
                <div style={{ color: C.muted, fontSize: 10, textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: 6 }}>
                  {selected.position} · {selected.team_name || "Free Agent"}
                </div>
                <h2 style={{ color: C.white, margin: 0, fontSize: 22, fontWeight: 700, letterSpacing: "-0.02em" }}>{selected.name}</h2>
              </div>
              <div style={{ display: "flex", gap: 6 }}>
                <Pill color={C.accent}>{selected.position}</Pill>
                <Pill color={C.success}>{selected.player_efficiency_rating} PER</Pill>
              </div>
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(6, 1fr)", gap: 12 }}>
              {[
                { l: "PPG", v: selected.points_per_game, accent: true },
                { l: "APG", v: selected.assists_per_game },
                { l: "RPG", v: selected.rebounds_per_game },
                { l: "FG%", v: (selected.field_goal_pct * 100).toFixed(1) + "%" },
                { l: "3P%", v: (selected.three_point_pct * 100).toFixed(1) + "%" },
                { l: "TS%", v: (selected.true_shooting_pct * 100).toFixed(1) + "%" },
              ].map(s => (
                <div key={s.l} style={{ textAlign: "center", background: C.surface, borderRadius: 6, padding: "12px 8px", border: `1px solid ${C.border}` }}>
                  <div style={{ color: s.accent ? C.accent : C.white, fontSize: 20, fontWeight: 700, lineHeight: 1 }}>{s.v}</div>
                  <div style={{ color: C.muted2, fontSize: 10, marginTop: 5, textTransform: "uppercase", letterSpacing: "0.05em" }}>{s.l}</div>
                </div>
              ))}
            </div>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, marginBottom: 16 }}>
            {radar && (
              <div style={{ background: C.card, border: `1px solid ${C.border}`, borderRadius: 8, padding: 20 }}>
                <SectionHeader title="Skill Radar" sub="Normalized across league" />
                <ResponsiveContainer width="100%" height={240}>
                  <RadarChart data={radar.stats} margin={{ top: 0, right: 20, bottom: 0, left: 20 }}>
                    <PolarGrid stroke={C.border} />
                    <PolarAngleAxis dataKey="stat" tick={{ fill: C.muted, fontSize: 11 }} />
                    <PolarRadiusAxis angle={30} domain={[0, 100]} tick={false} axisLine={false} />
                    <Radar dataKey="value" stroke={C.accent} fill={C.accent} fillOpacity={0.2} strokeWidth={2} />
                  </RadarChart>
                </ResponsiveContainer>
              </div>
            )}

            {zones?.zones && (
              <div style={{ background: C.card, border: `1px solid ${C.border}`, borderRadius: 8, padding: 20 }}>
                <SectionHeader title="Shot Zones" sub="FG% by court region" />
                <ResponsiveContainer width="100%" height={240}>
                  <BarChart data={zones.zones} margin={{ top: 0, right: 0, left: -24, bottom: 50 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke={C.border} vertical={false} />
                    <XAxis dataKey="zone" stroke="none" tick={{ fill: C.muted, fontSize: 9 }} angle={-35} textAnchor="end" />
                    <YAxis stroke="none" tick={{ fill: C.muted, fontSize: 10 }} tickFormatter={v => (v * 100).toFixed(0) + "%"} />
                    <Tooltip contentStyle={{ background: C.card2, border: `1px solid ${C.border}`, borderRadius: 6, fontSize: 12 }}
                      formatter={(v, n) => n === "fg_pct" ? [(v * 100).toFixed(1) + "%", "FG%"] : [v, n]} />
                    <Bar dataKey="fg_pct" name="FG%" fill={C.accent} radius={[3, 3, 0, 0]} opacity={0.85} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}
          </div>

          {perf && (
            <div style={{ background: C.card, border: `1px solid ${C.border}`, borderRadius: 8, padding: 20 }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
                <SectionHeader title="Performance Projection" sub="Next game estimate based on context" />
                <Pill color={perf.matchup_difficulty === "Tough" ? C.danger : perf.matchup_difficulty === "Easy" ? C.success : C.warning}>
                  {perf.matchup_difficulty} Matchup
                </Pill>
              </div>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(5, 1fr)", gap: 10 }}>
                {[
                  { l: "Points", v: perf.predicted_points },
                  { l: "Assists", v: perf.predicted_assists },
                  { l: "Rebounds", v: perf.predicted_rebounds },
                  { l: "3PM", v: perf.predicted_threes },
                  { l: "PER", v: perf.predicted_efficiency },
                ].map(s => (
                  <div key={s.l} style={{ textAlign: "center", background: C.surface, borderRadius: 6, padding: "14px 8px", border: `1px solid ${C.border}` }}>
                    <div style={{ color: C.accent, fontSize: 22, fontWeight: 700, lineHeight: 1 }}>{s.v}</div>
                    <div style={{ color: C.muted2, fontSize: 10, marginTop: 5, textTransform: "uppercase", letterSpacing: "0.05em" }}>{s.l}</div>
                  </div>
                ))}
              </div>
              <div style={{ color: C.muted2, fontSize: 10, marginTop: 10 }}>
                95% CI: {perf.confidence_interval.lower} — {perf.confidence_interval.upper} pts
              </div>
            </div>
          )}
        </div>
      ) : (
        <div style={{ display: "flex", alignItems: "center", justifyContent: "center", color: C.muted2, fontSize: 13 }}>
          Select a player to view analytics
        </div>
      )}
    </div>
  );
};

// ── TAB: Similarity ───────────────────────────────────────────
const SimilarityTab = () => {
  const [players, setPlayers] = useState([]);
  const [selectedId, setSelectedId] = useState("");
  const [result, setResult] = useState(null);
  const [clusterData, setClusterData] = useState([]);
  const [loading, setLoading] = useState(false);

  const CLUSTER_COLORS = [C.accent, "#A78BFA", C.success, C.warning, C.danger, "#22D3EE"];

  useEffect(() => {
    api.getPlayers({ page_size: 40, sort_by: "points_per_game" }).then(d => setPlayers(d.items || []));
    api.getClusterData().then(d => setClusterData(d.players || [])).catch(() => {});
  }, []);

  const handleFind = () => {
    if (!selectedId) return;
    setLoading(true);
    api.getPlayerSimilarity({ player_id: parseInt(selectedId), top_n: 6 })
      .then(r => { setResult(r); setLoading(false); })
      .catch(() => setLoading(false));
  };

  return (
    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
      <div>
        <div style={{ background: C.card, border: `1px solid ${C.border}`, borderRadius: 8, padding: 20, marginBottom: 16 }}>
          <SectionHeader title="Player Similarity" sub="K-Means clustering · cosine similarity" />
          <select value={selectedId} onChange={e => setSelectedId(e.target.value)} style={{ ...selectStyle, marginBottom: 12 }}>
            <option value="">Select a player...</option>
            {players.map(p => <option key={p.id} value={p.id}>{p.name} ({p.position} · {p.team_name})</option>)}
          </select>
          <button onClick={handleFind} disabled={!selectedId || loading} style={{ ...btnPrimary, opacity: !selectedId || loading ? 0.5 : 1 }}>
            {loading ? "Searching..." : "Find Similar Players"}
          </button>
        </div>

        {result && (
          <div style={{ background: C.card, border: `1px solid ${C.border}`, borderRadius: 8, overflow: "hidden" }}>
            <div style={{ padding: "14px 20px", borderBottom: `1px solid ${C.border}`, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <div style={{ color: C.white, fontWeight: 600, fontSize: 13 }}>Similar to {result.target_player}</div>
              <Pill color={C.accent}>Cluster #{result.cluster}</Pill>
            </div>
            {result.similar_players.map((p, i) => (
              <div key={p.player_id} style={{
                padding: "14px 20px",
                borderBottom: i < result.similar_players.length - 1 ? `1px solid ${C.border}` : "none",
                borderLeft: `2px solid ${CLUSTER_COLORS[p.cluster % 6]}`,
              }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
                  <div>
                    <div style={{ color: C.text, fontWeight: 500, fontSize: 13 }}>{p.player_name}</div>
                    <div style={{ color: C.muted2, fontSize: 10, marginTop: 1 }}>{p.team_name} · {p.position}</div>
                  </div>
                  <div style={{ textAlign: "right" }}>
                    <div style={{ color: C.success, fontWeight: 700, fontSize: 15 }}>{(p.similarity_score * 100).toFixed(1)}%</div>
                    <div style={{ color: C.muted2, fontSize: 10 }}>similarity</div>
                  </div>
                </div>
                <div style={{ display: "flex", gap: 16 }}>
                  {[{ l: "PPG", v: p.points_per_game }, { l: "APG", v: p.assists_per_game }, { l: "RPG", v: p.rebounds_per_game }, { l: "PER", v: p.player_efficiency_rating }].map(s => (
                    <div key={s.l}>
                      <div style={{ color: C.muted, fontSize: 11, fontWeight: 600 }}>{s.v}</div>
                      <div style={{ color: C.muted2, fontSize: 9, textTransform: "uppercase", letterSpacing: "0.05em" }}>{s.l}</div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <div style={{ background: C.card, border: `1px solid ${C.border}`, borderRadius: 8, padding: 20 }}>
        <SectionHeader title="Player Cluster Map" sub="2D PCA projection of statistical feature vectors" />
        {clusterData.length > 0 ? (
          <>
            <ResponsiveContainer width="100%" height={360}>
              <ScatterChart margin={{ top: 10, right: 10, bottom: 10, left: 10 }}>
                <CartesianGrid strokeDasharray="3 3" stroke={C.border} />
                <XAxis type="number" dataKey="x" name="PC1" stroke="none" tick={{ fill: C.muted, fontSize: 10 }} />
                <YAxis type="number" dataKey="y" name="PC2" stroke="none" tick={{ fill: C.muted, fontSize: 10 }} />
                <Tooltip contentStyle={{ background: C.card2, border: `1px solid ${C.border}`, borderRadius: 6, fontSize: 12 }}
                  content={({ payload }) => {
                    if (!payload?.length) return null;
                    const d = payload[0].payload;
                    return (
                      <div style={{ background: C.card2, border: `1px solid ${C.border}`, borderRadius: 6, padding: "8px 12px", fontSize: 12 }}>
                        <div style={{ color: C.white, fontWeight: 600 }}>{d.name}</div>
                        <div style={{ color: C.muted, marginTop: 2 }}>{d.position} · {d.cluster_label}</div>
                        <div style={{ color: C.accent, marginTop: 2 }}>{d.ppg} PPG</div>
                      </div>
                    );
                  }} />
                {[0, 1, 2, 3, 4, 5].map(cluster => (
                  <Scatter key={cluster} data={clusterData.filter(d => d.cluster === cluster)} fill={CLUSTER_COLORS[cluster]} opacity={0.8} />
                ))}
              </ScatterChart>
            </ResponsiveContainer>
            <div style={{ display: "flex", flexWrap: "wrap", gap: 10, marginTop: 10 }}>
              {["Scoring Guard", "Playmaking Big", "3-and-D Wing", "Point Guard", "Interior", "Versatile FW"].map((l, i) => (
                <div key={l} style={{ display: "flex", alignItems: "center", gap: 5, fontSize: 10, color: C.muted }}>
                  <div style={{ width: 6, height: 6, borderRadius: "50%", background: CLUSTER_COLORS[i] }} />{l}
                </div>
              ))}
            </div>
          </>
        ) : (
          <div style={{ color: C.muted2, textAlign: "center", padding: 40, fontSize: 13 }}>
            Train models first to view cluster visualization
          </div>
        )}
      </div>
    </div>
  );
};

// ── TAB: Models ───────────────────────────────────────────────
const ModelsTab = () => {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getModelMetrics().then(setMetrics).catch(() => {}).finally(() => setLoading(false));
  }, []);

  if (loading) return <Loader />;
  if (!metrics) return (
    <div style={{ textAlign: "center", padding: 80, color: C.muted }}>
      <Icon name="model" size={40} color={C.border} />
      <div style={{ fontSize: 16, color: C.text, fontWeight: 600, marginTop: 16, marginBottom: 8 }}>Models Not Trained</div>
      <div style={{ fontSize: 13 }}>Run <code style={{ background: C.card, padding: "2px 8px", borderRadius: 4, color: C.accent }}>docker compose up</code> to train automatically.</div>
    </div>
  );

  const modelData = metrics.shot_probability_models.map(m => ({
    name: m.model_name,
    Accuracy: +(m.accuracy * 100).toFixed(1),
    "ROC-AUC": +(m.roc_auc * 100).toFixed(1),
    F1: +(m.f1_score * 100).toFixed(1),
  }));

  const fiData = Object.entries(metrics.feature_importance || {}).slice(0, 10)
    .map(([f, v]) => ({ feature: f.replace(/_/g, " "), importance: +(v * 100).toFixed(2) }));

  return (
    <div>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 12, marginBottom: 20 }}>
        <StatCard label="Best Model" value={metrics.best_model.replace(/_/g, " ").toUpperCase()} sub="Highest ROC-AUC" icon="star" accent />
        <StatCard label="Trained" value={metrics.training_date} sub="Last run" icon="chart" />
        <StatCard label="Models" value={metrics.shot_probability_models.length} sub="LR · RF · XGBoost" icon="model" />
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16, marginBottom: 16 }}>
        <div style={{ background: C.card, border: `1px solid ${C.border}`, borderRadius: 8, padding: 20 }}>
          <SectionHeader title="Model Comparison" sub="Shot make probability classification task" />
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={modelData} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke={C.border} vertical={false} />
              <XAxis dataKey="name" stroke="none" tick={{ fill: C.muted, fontSize: 10 }} />
              <YAxis stroke="none" tick={{ fill: C.muted, fontSize: 10 }} domain={[60, 80]} tickFormatter={v => v + "%"} />
              <Tooltip contentStyle={{ background: C.card2, border: `1px solid ${C.border}`, borderRadius: 6 }} formatter={v => v + "%"} />
              <Legend wrapperStyle={{ color: C.muted, fontSize: 11 }} />
              <Bar dataKey="Accuracy" fill={C.accent} radius={[3, 3, 0, 0]} />
              <Bar dataKey="ROC-AUC" fill={C.success} radius={[3, 3, 0, 0]} />
              <Bar dataKey="F1" fill="#A78BFA" radius={[3, 3, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div style={{ background: C.card, border: `1px solid ${C.border}`, borderRadius: 8, padding: 20 }}>
          <SectionHeader title="Feature Importance" sub="XGBoost — what drives shot probability" />
          {fiData.map((f, i) => (
            <div key={f.feature} style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 9 }}>
              <div style={{ color: C.muted, width: 175, fontSize: 11 }}>{f.feature}</div>
              <div style={{ flex: 1, background: C.border, borderRadius: 2, height: 5 }}>
                <div style={{
                  width: `${(f.importance / fiData[0].importance) * 100}%`,
                  background: i === 0 ? C.accent : `hsl(${30 + i * 15}, 70%, 55%)`,
                  borderRadius: 2, height: "100%",
                }} />
              </div>
              <div style={{ color: C.muted, fontSize: 10, width: 36, textAlign: "right" }}>{f.importance}%</div>
            </div>
          ))}
        </div>
      </div>

      <div style={{ background: C.card, border: `1px solid ${C.border}`, borderRadius: 8, overflow: "hidden" }}>
        <div style={{ padding: "14px 20px", borderBottom: `1px solid ${C.border}` }}>
          <SectionHeader title="Detailed Metrics" sub="Full classification report per model" />
        </div>
        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 12 }}>
          <thead>
            <tr style={{ background: C.surface }}>
              {["Model", "Accuracy", "ROC-AUC", "Precision", "Recall", "F1 Score", ""].map(h => (
                <th key={h} style={{
                  padding: "10px 20px", textAlign: h === "Model" ? "left" : "center",
                  color: C.muted, fontWeight: 500, fontSize: 10, textTransform: "uppercase",
                  letterSpacing: "0.05em", borderBottom: `1px solid ${C.border}`,
                }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {metrics.shot_probability_models.map((m, i) => (
              <tr key={m.model_name} style={{ borderBottom: `1px solid ${C.border}`, background: i % 2 === 0 ? "transparent" : C.surface + "60" }}>
                <td style={{ padding: "12px 20px", color: C.text, fontWeight: 500 }}>{m.model_name}</td>
                {[m.accuracy, m.roc_auc, m.precision, m.recall, m.f1_score].map((v, j) => (
                  <td key={j} style={{ padding: "12px 20px", textAlign: "center", color: v > 0.65 ? C.success : C.muted, fontWeight: 600 }}>
                    {(v * 100).toFixed(1)}%
                  </td>
                ))}
                <td style={{ padding: "12px 20px", textAlign: "center" }}>
                  {m.model_name.toLowerCase().replace(/ /g, "_") === metrics.best_model
                    ? <Pill color={C.success}>Best</Pill>
                    : <Pill color={C.muted2}>Trained</Pill>}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

// ── Logo SVG (matches brand) ──────────────────────────────────
const Logo = () => (
  <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
    <svg width="32" height="32" viewBox="0 0 100 100">
      <circle cx="50" cy="50" r="48" fill="none" stroke={C.accent} strokeWidth="3" opacity="0.3"/>
      <text x="50" y="62" textAnchor="middle" fontSize="38" fontWeight="800" fontFamily="system-ui" fill={C.white}>H</text>
      <circle cx="50" cy="50" r="30" fill="none" stroke={C.accent} strokeWidth="2" opacity="0.2"/>
    </svg>
    <div>
      <div style={{ fontSize: 16, fontWeight: 800, letterSpacing: "-0.03em", lineHeight: 1 }}>
        <span style={{ color: C.white }}>hoop</span>
        <span style={{ color: C.accent }}>mind</span>
        <span style={{ color: C.white }}>-ai</span>
      </div>
      <div style={{ color: C.muted2, fontSize: 9, letterSpacing: "0.12em", textTransform: "uppercase", marginTop: 3 }}>
        NBA Analytics
      </div>
    </div>
  </div>
);

// ── App ───────────────────────────────────────────────────────
export default function App() {
  const [activeTab, setActiveTab] = useState(0);

  const TAB_COMPONENTS = [OverviewTab, ShotAnalyticsTab, PlayersTab, SimilarityTab, ModelsTab];
  const ActiveComponent = TAB_COMPONENTS[activeTab];

  return (
    <div style={{ minHeight: "100vh", background: C.bg, color: C.text, fontFamily: "'Inter', system-ui, -apple-system, sans-serif" }}>
      {/* Header */}
      <header style={{ background: C.surface, borderBottom: `1px solid ${C.border}`, padding: "0 32px", position: "sticky", top: 0, zIndex: 100 }}>
        <div style={{ maxWidth: 1400, margin: "0 auto", display: "flex", alignItems: "center", height: 60 }}>
          <div style={{ marginRight: 48 }}>
            <Logo />
          </div>
          <nav style={{ display: "flex", gap: 2 }}>
            {TABS.map(tab => (
              <button key={tab.id} onClick={() => setActiveTab(tab.id)} style={{
                background: activeTab === tab.id ? C.accentDim : "transparent",
                color: activeTab === tab.id ? C.accent : C.muted,
                border: "none",
                borderRadius: 6, padding: "6px 16px", fontSize: 12, fontWeight: activeTab === tab.id ? 600 : 400,
                cursor: "pointer", transition: "all 0.1s", letterSpacing: "0.01em",
              }}>{tab.label}</button>
            ))}
          </nav>
          <div style={{ marginLeft: "auto", display: "flex", alignItems: "center", gap: 8 }}>
            <div style={{ width: 6, height: 6, borderRadius: "50%", background: C.success }} />
            <span style={{ color: C.muted2, fontSize: 11 }}>Live</span>
          </div>
        </div>
      </header>

      {/* Breadcrumb */}
      <div style={{ borderBottom: `1px solid ${C.border}`, background: C.surface, padding: "0 32px" }}>
        <div style={{ maxWidth: 1400, margin: "0 auto", height: 36, display: "flex", alignItems: "center", gap: 8 }}>
          <span style={{ color: C.muted2, fontSize: 11 }}>HoopMind AI</span>
          <span style={{ color: C.border }}>›</span>
          <span style={{ color: C.muted, fontSize: 11 }}>{TABS[activeTab].label}</span>
        </div>
      </div>

      {/* Content */}
      <main style={{ maxWidth: 1400, margin: "0 auto", padding: "24px 32px" }}>
        <ActiveComponent />
      </main>

      {/* Footer */}
      <footer style={{ borderTop: `1px solid ${C.border}`, padding: "14px 32px", marginTop: 40 }}>
        <div style={{ maxWidth: 1400, margin: "0 auto", display: "flex", justifyContent: "space-between", color: C.muted2, fontSize: 11 }}>
          <div>HoopMind AI · NBA Analytics Platform</div>
          <div>FastAPI · XGBoost · React · 2023–24</div>
        </div>
      </footer>
    </div>
  );
}
