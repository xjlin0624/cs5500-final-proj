import React, { useEffect, useMemo, useState } from "react";
import { getSavingsSummary } from "../api";
import StatCard from "../components/StatCard";
import BarSavingsChart from "../components/BarSavingsChart";

function formatMoney(value) {
  const n = Number(value || 0);
  return `$${n.toFixed(2)}`;
}

function formatActionType(value) {
  return String(value || "unknown").replaceAll("_", " ").replace(/^\w/, (c) => c.toUpperCase());
}

function groupByMonth(history) {
  const map = {};
  for (const entry of history) {
    if (!entry.was_successful || !entry.recovered_value) continue;
    const d = new Date(entry.logged_at);
    const label = d.toLocaleString("en-US", { month: "short", year: "numeric" });
    map[label] = (map[label] || 0) + Number(entry.recovered_value);
  }
  return Object.entries(map)
    .sort((a, b) => new Date(a[0]) - new Date(b[0]))
    .map(([month, amount]) => ({ month, amount: parseFloat(amount.toFixed(2)) }));
}

export default function Savings() {
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState("");

  useEffect(() => {
    async function load() {
      try {
        setLoading(true);
        setErrorMsg("");
        const data = await getSavingsSummary();
        setSummary(data);
      } catch (err) {
        setErrorMsg(err.message || "Failed to load savings");
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  const stats = useMemo(() => {
    if (!summary) return [];
    const avg =
      summary.successful_actions > 0
        ? summary.total_recovered / summary.successful_actions
        : 0;
    return [
      { title: "Total Saved", value: formatMoney(summary.total_recovered), trend: "from successful actions", positive: true },
      { title: "Successful Actions", value: String(summary.successful_actions), trend: `of ${summary.total_actions} total`, positive: true },
      { title: "Avg Savings / Action", value: formatMoney(avg), trend: "per successful action", positive: true },
    ];
  }, [summary]);

  const chartData = useMemo(() => {
    if (!summary) return [];
    return groupByMonth(summary.history);
  }, [summary]);

  const history = summary?.history ?? [];

  return (
    <div className="page-content">
      {loading && <p>Loading savings...</p>}
      {errorMsg && <p style={{ color: "red" }}>{errorMsg}</p>}

      <div className="three-col-grid">
        {stats.map((item) => (
          <StatCard key={item.title} {...item} />
        ))}
      </div>

      <div className="section-space"></div>

      {chartData.length > 0 ? (
        <BarSavingsChart data={chartData} />
      ) : (
        !loading && <p style={{ color: "#9ca3af", fontSize: "0.85rem" }}>No savings chart data yet.</p>
      )}

      <div className="section-space"></div>

      <div className="table-card">
        <div className="table-card-header left-only">
          <div>
            <div className="section-card-title">Savings History</div>
            <div className="section-card-subtitle">
              Detailed breakdown of all your savings
            </div>
          </div>
        </div>

        <table className="data-table">
          <thead>
            <tr>
              <th>DATE</th>
              <th>ACTION</th>
              <th>RECOVERED</th>
              <th>STATUS</th>
            </tr>
          </thead>
          <tbody>
            {history.length === 0 && !loading ? (
              <tr>
                <td colSpan="4">No savings history yet.</td>
              </tr>
            ) : (
              history.map((row) => (
                <tr key={row.id}>
                  <td>{new Date(row.logged_at).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" })}</td>
                  <td>{formatActionType(row.action_taken)}</td>
                  <td className="green-text strong-text">
                    {row.recovered_value != null ? formatMoney(row.recovered_value) : "—"}
                  </td>
                  <td>
                    <span className={row.was_successful ? "type-pill green" : "type-pill blue"}>
                      {row.was_successful ? "Success" : "Pending"}
                    </span>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
