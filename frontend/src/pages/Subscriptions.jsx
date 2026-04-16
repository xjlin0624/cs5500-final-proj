import React, { useEffect, useMemo, useState } from "react";

import { getSubscriptions } from "../api";
import StatCard from "../components/StatCard";

function normalizeSubscriptions(data) {
  if (Array.isArray(data)) return data;
  return data.subscriptions || data.results || data.data || [];
}

function formatDate(value) {
  if (!value) return "Not available";
  return new Date(value).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

function formatMoney(value) {
  if (value === null || value === undefined) return "Not available";
  return `$${Number(value).toFixed(2)}`;
}

function formatLabel(value) {
  return String(value || "unknown")
    .replaceAll("_", " ")
    .replace(/^\w/, (char) => char.toUpperCase());
}

function getCancellationSteps(subscription) {
  if (Array.isArray(subscription.cancellation_steps_list)) {
    return subscription.cancellation_steps_list;
  }
  if (subscription.cancellation_steps) {
    return String(subscription.cancellation_steps)
      .split("\n")
      .map((step) => step.trim())
      .filter(Boolean);
  }
  return [];
}

export default function Subscriptions() {
  const [subscriptions, setSubscriptions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState("");

  useEffect(() => {
    async function loadSubscriptions() {
      try {
        setLoading(true);
        setErrorMsg("");
        const data = await getSubscriptions();
        setSubscriptions(normalizeSubscriptions(data));
      } catch (error) {
        setErrorMsg(error.message || "Failed to load subscriptions.");
      } finally {
        setLoading(false);
      }
    }

    loadSubscriptions();
  }, []);

  const stats = useMemo(() => {
    const withUpcomingCharge = subscriptions.filter(
      (subscription) => subscription.next_expected_charge
    ).length;
    const withGuidance = subscriptions.filter(
      (subscription) =>
        subscription.cancellation_url || getCancellationSteps(subscription).length > 0
    ).length;
    const estimatedMonthlyCost = subscriptions.reduce(
      (sum, subscription) => sum + Number(subscription.estimated_monthly_cost || 0),
      0
    );

    return [
      {
        title: "Detected Subscriptions",
        value: String(subscriptions.length),
        trend:
          subscriptions.length > 0
            ? "Recurring charges found from your order history"
            : "No recurring purchases detected yet",
        positive: subscriptions.length > 0,
      },
      {
        title: "Upcoming Charges",
        value: String(withUpcomingCharge),
        trend:
          withUpcomingCharge > 0
            ? "Next expected charge is available"
            : "No next charge dates calculated yet",
        positive: withUpcomingCharge > 0,
      },
      {
        title: "Estimated Monthly Cost",
        value: formatMoney(estimatedMonthlyCost),
        trend:
          withGuidance > 0
            ? `${withGuidance} subscription${withGuidance === 1 ? "" : "s"} include cancellation guidance`
            : "Cancellation guidance is not available yet",
        positive: withGuidance > 0,
      },
    ];
  }, [subscriptions]);

  return (
    <div className="page-content">
      {loading && <p>Loading subscriptions...</p>}
      {errorMsg && <p style={{ color: "red" }}>{errorMsg}</p>}

      <div className="three-col-grid">
        {stats.map((item) => (
          <StatCard key={item.title} {...item} />
        ))}
      </div>

      <div className="section-space"></div>

      <div className="table-card">
        <div className="table-card-header left-only">
          <div>
            <div className="section-card-title">Recurring Subscription Monitor</div>
            <div className="section-card-subtitle">
              Review upcoming charges and retailer-specific cancellation steps.
            </div>
          </div>
        </div>

        {subscriptions.length === 0 && !loading ? (
          <p style={{ color: "#6b7280", margin: 0 }}>
            No recurring subscriptions have been detected yet. Once AfterCart identifies a
            recurring purchase pattern, this page will show the retailer, next expected
            charge, and cancellation guidance.
          </p>
        ) : (
          <div style={{ display: "grid", gap: "16px" }}>
            {subscriptions.map((subscription) => {
              const steps = getCancellationSteps(subscription);

              return (
                <div
                  key={subscription.id}
                  style={{
                    border: "1px solid #ececec",
                    borderRadius: "12px",
                    padding: "16px",
                    display: "grid",
                    gap: "12px",
                  }}
                >
                  <div style={{ display: "flex", justifyContent: "space-between", gap: "16px" }}>
                    <div>
                      <div className="section-card-title">{subscription.product_name}</div>
                      <div className="section-card-subtitle">
                        {formatLabel(subscription.retailer)} | Source:{" "}
                        {formatLabel(subscription.detection_method)}
                      </div>
                    </div>
                    <span className="type-pill blue">{formatLabel(subscription.status)}</span>
                  </div>

                  <div className="summary-row">
                    <span>Next expected charge</span>
                    <strong>{formatDate(subscription.next_expected_charge)}</strong>
                  </div>
                  <div className="summary-row">
                    <span>Last charged</span>
                    <strong>{formatDate(subscription.last_charged_at)}</strong>
                  </div>
                  <div className="summary-row">
                    <span>Estimated monthly cost</span>
                    <strong>{formatMoney(subscription.estimated_monthly_cost)}</strong>
                  </div>

                  <div className="summary-divider"></div>

                  <div>
                    <div className="section-card-title" style={{ fontSize: "0.95rem" }}>
                      Cancellation Guidance
                    </div>
                    {subscription.cancellation_url ? (
                      <p style={{ marginBottom: "8px" }}>
                        <a href={subscription.cancellation_url} target="_blank" rel="noreferrer">
                          Open cancellation page
                        </a>
                      </p>
                    ) : (
                      <p style={{ color: "#6b7280", marginBottom: "8px" }}>
                        No cancellation URL is available for this retailer yet.
                      </p>
                    )}

                    {steps.length > 0 ? (
                      <ol style={{ margin: 0, paddingLeft: "20px" }}>
                        {steps.map((step, index) => (
                          <li key={`${subscription.id}-step-${index}`}>{step}</li>
                        ))}
                      </ol>
                    ) : (
                      <p style={{ color: "#6b7280", margin: 0 }}>
                        No step-by-step cancellation instructions are available yet.
                      </p>
                    )}

                    {subscription.cancellation_notes ? (
                      <p style={{ marginTop: "8px", color: "#6b7280" }}>
                        {subscription.cancellation_notes}
                      </p>
                    ) : null}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
