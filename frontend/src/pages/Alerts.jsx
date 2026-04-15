import React, { useEffect, useMemo, useState } from "react";
import { dismissAlert, getAlerts, resolveAlert } from "../api";

function normalizeAlerts(data) {
  if (Array.isArray(data)) return data;
  return data.alerts || data.results || data.data || data.value || [];
}

function formatCurrency(value) {
  const amount = Number(value);
  return Number.isFinite(amount) ? `$${amount.toFixed(2)}` : null;
}

function formatAlertType(value) {
  const text = String(value || "alert").replaceAll("_", " ");
  return text.charAt(0).toUpperCase() + text.slice(1);
}

function formatEvidence(alert) {
  const evidence =
    alert && typeof alert.evidence === "object" && alert.evidence !== null
      ? alert.evidence
      : null;

  if (!evidence) {
    return "No additional evidence.";
  }

  if (alert.alert_type === "price_drop") {
    const current = formatCurrency(evidence.current_price);
    const paid = formatCurrency(evidence.paid_price);
    const delta = formatCurrency(evidence.price_delta);

    if (current && paid && delta) {
      return `Now ${current}, paid ${paid}, potential savings ${delta}.`;
    }
    if (current && paid) {
      return `Now ${current}, paid ${paid}.`;
    }
  }

  if (alert.alert_type === "delivery_anomaly") {
    if (evidence.event_type === "eta_updated") {
      return `ETA changed from ${evidence.previous_eta || "unknown"} to ${evidence.new_eta || "unknown"}.`;
    }
    if (evidence.event_type === "tracking_stalled") {
      return "Tracking appears to be stalled.";
    }
  }

  return Object.entries(evidence)
    .map(([key, value]) => `${key}: ${Array.isArray(value) ? value.join(", ") : String(value)}`)
    .join(" | ");
}

function mapAlert(alert, index) {
  const priority = String(alert.priority || "medium");
  const status = String(alert.status || "unknown");

  return {
    id: alert.id || alert.alert_id || index,
    title: alert.title || formatAlertType(alert.alert_type),
    meta: `${formatAlertType(alert.alert_type)} | ${priority.toUpperCase()}`,
    evidence: formatEvidence(alert),
    message: String(alert.body || "No message available."),
    active: status !== "dismissed" && status !== "resolved",
    activeLabel: status.charAt(0).toUpperCase() + status.slice(1),
  };
}

export default function Alerts() {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState("");

  async function loadAlerts() {
    try {
      setLoading(true);
      setErrorMsg("");
      const res = await getAlerts();
      setAlerts(normalizeAlerts(res));
    } catch (error) {
      setErrorMsg(error.message || "Failed to load alerts");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadAlerts();
  }, []);

  async function handleResolve(id) {
    try {
      await resolveAlert(id);
      await loadAlerts();
    } catch (error) {
      setErrorMsg(error.message || "Failed to resolve alert");
    }
  }

  async function handleDismiss(id) {
    try {
      await dismissAlert(id);
      await loadAlerts();
    } catch (error) {
      setErrorMsg(error.message || "Failed to dismiss alert");
    }
  }

  const mappedAlerts = useMemo(() => alerts.map(mapAlert), [alerts]);

  return (
    <div className="page-content">
      {loading && <p>Loading alerts...</p>}
      {errorMsg && <p style={{ color: "red" }}>{errorMsg}</p>}

      <div className="page-helper-row">
        <div className="page-helper-text">
          Review price drops and delivery issues that need your attention.
        </div>
        <button className="primary-btn" type="button">
          + Create New Alert
        </button>
      </div>

      <div className="pill-tabs">
        <button className="pill-tab active" type="button">
          Active Alerts
        </button>
        <button className="pill-tab" type="button">
          Triggered Alerts
        </button>
      </div>

      <div className="three-col-grid alerts-grid">
        {mappedAlerts.length === 0 && !loading ? (
          <p>No alerts found.</p>
        ) : (
          mappedAlerts.map((item) => (
            <div className="alert-card" key={item.id}>
              <div className="alert-card-top">
                <div className="alert-image-box">!</div>
                <div>
                  <div className="alert-product">{item.title}</div>
                  <div className="alert-store">{item.meta}</div>
                </div>
              </div>

              <div className="alert-info-list">
                <div className="alert-info-row">
                  <span>Evidence</span>
                  <strong>{item.evidence}</strong>
                </div>
                <div className="alert-info-row">
                  <span>Message</span>
                  <strong>{item.message}</strong>
                </div>
              </div>

              <div className="alert-actions-row">
                <span className="mini-status">
                  {item.active ? `Active: ${item.activeLabel}` : item.activeLabel}
                </span>
                <div className="alert-action-buttons">
                  <button
                    className="secondary-btn"
                    type="button"
                    onClick={() => handleResolve(item.id)}
                  >
                    Resolve
                  </button>
                  <button
                    className="danger-text-btn"
                    type="button"
                    onClick={() => handleDismiss(item.id)}
                  >
                    Dismiss
                  </button>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
