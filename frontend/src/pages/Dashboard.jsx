import React, { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";

import {
  getAlerts,
  getOrders,
  getPriceHistory,
  getSavingsSummary,
  getSubscriptions,
} from "../api";
import PriceLineChart from "../components/PriceLineChart";
import StatCard from "../components/StatCard";

function normalizeOrders(data) {
  if (Array.isArray(data)) return data;
  return data.orders || data.results || data.data || [];
}

function normalizeAlerts(data) {
  if (Array.isArray(data)) return data;
  return data.alerts || data.results || data.data || [];
}

function normalizeSubscriptions(data) {
  if (Array.isArray(data)) return data;
  return data.subscriptions || data.results || data.data || [];
}

function formatMoney(value) {
  return `$${Number(value || 0).toFixed(2)}`;
}

function formatDate(value) {
  if (!value) return "N/A";
  return new Date(value).toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });
}

function mapRecentPurchase(order) {
  const firstItem =
    Array.isArray(order.items) && order.items.length > 0 ? order.items[0] : null;

  return {
    id: order.id || order.retailer_order_id,
    store: order.retailer || "Unknown",
    product: firstItem?.product_name || "Unknown item",
    price: formatMoney(order.subtotal || 0),
    status: order.order_status || "Unknown",
    date: formatDate(order.order_date),
  };
}

function getStatusClass(status) {
  const value = String(status || "").toLowerCase();
  if (value.includes("deliver")) return "delivered";
  if (value.includes("ship")) return "shipped";
  if (value.includes("delay")) return "delayed";
  if (value.includes("track")) return "tracking";
  if (value.includes("alert")) return "alert";
  return "tracking";
}

function pickFeaturedItem(orders) {
  for (const order of orders) {
    for (const item of order.items || []) {
      if (item?.id) {
        return item;
      }
    }
  }
  return null;
}

function buildChartData(history) {
  if (!Array.isArray(history)) return [];
  return history
    .slice()
    .reverse()
    .map((snapshot) => ({
      label: formatDate(snapshot.scraped_at),
      price: Number(snapshot.scraped_price || 0),
    }))
    .filter((point) => Number.isFinite(point.price));
}

export default function Dashboard() {
  const [orders, setOrders] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [savings, setSavings] = useState(null);
  const [subscriptions, setSubscriptions] = useState([]);
  const [chartData, setChartData] = useState([]);
  const [featuredItemName, setFeaturedItemName] = useState("");
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState("");

  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true);
        setErrorMsg("");

        const [ordersRes, alertsRes, savingsRes, subscriptionsRes] = await Promise.all([
          getOrders(),
          getAlerts(),
          getSavingsSummary(),
          getSubscriptions(),
        ]);

        const nextOrders = normalizeOrders(ordersRes);
        setOrders(nextOrders);
        setAlerts(normalizeAlerts(alertsRes));
        setSavings(savingsRes);
        setSubscriptions(normalizeSubscriptions(subscriptionsRes));

        const featuredItem = pickFeaturedItem(nextOrders);
        if (featuredItem?.id) {
          try {
            const history = await getPriceHistory(featuredItem.id, 20);
            setChartData(buildChartData(history));
            setFeaturedItemName(featuredItem.product_name || "Tracked item");
          } catch {
            setChartData([]);
            setFeaturedItemName(featuredItem.product_name || "Tracked item");
          }
        } else {
          setChartData([]);
          setFeaturedItemName("");
        }
      } catch (error) {
        setErrorMsg(error.message || "Failed to load dashboard data");
      } finally {
        setLoading(false);
      }
    }

    loadData();
  }, []);

  const activeAlerts = useMemo(
    () =>
      alerts.filter((alert) => {
        const status = String(alert.status || "").toLowerCase();
        return status !== "resolved" && status !== "dismissed";
      }),
    [alerts]
  );

  const upcomingSubscription = useMemo(() => {
    return subscriptions
      .filter((subscription) => subscription.next_expected_charge)
      .sort(
        (a, b) =>
          new Date(a.next_expected_charge).getTime() -
          new Date(b.next_expected_charge).getTime()
      )[0];
  }, [subscriptions]);

  const stats = useMemo(() => {
    const totalRecovered = savings?.total_recovered || 0;
    const successfulActions = savings?.successful_actions || 0;
    const monitoredSubscriptions = subscriptions.length;

    return [
      {
        title: "Recovered Savings",
        value: formatMoney(totalRecovered),
        trend:
          successfulActions > 0
            ? `${successfulActions} successful outcome${successfulActions === 1 ? "" : "s"}`
            : "No recovered savings yet",
        positive: successfulActions > 0,
      },
      {
        title: "Active Alerts",
        value: String(activeAlerts.length),
        trend:
          activeAlerts.length > 0
            ? "Needs review"
            : "No unresolved alerts",
        positive: activeAlerts.length === 0,
      },
      {
        title: "Monitored Subscriptions",
        value: String(monitoredSubscriptions),
        trend: upcomingSubscription?.next_expected_charge
          ? `Next charge ${formatDate(upcomingSubscription.next_expected_charge)}`
          : "No upcoming recurring charges",
        positive: monitoredSubscriptions > 0,
      },
    ];
  }, [activeAlerts.length, savings, subscriptions, upcomingSubscription]);

  const recentPurchases = useMemo(() => {
    return orders.slice(0, 5).map(mapRecentPurchase);
  }, [orders]);

  const savingsSummary = useMemo(() => {
    if (!savings) {
      return {
        totalActions: 0,
        successfulActions: 0,
        breakdown: [],
      };
    }

    return {
      totalActions: savings.total_actions || 0,
      successfulActions: savings.successful_actions || 0,
      breakdown: (savings.by_action || []).slice(0, 3),
    };
  }, [savings]);

  return (
    <div className="page-content">
      {loading && <p>Loading dashboard...</p>}
      {errorMsg && <p style={{ color: "red" }}>{errorMsg}</p>}

      <section className="section-block">
        <div className="section-label">Overview</div>

        <div className="three-col-grid">
          {stats.map((item) => (
            <StatCard key={item.title} {...item} />
          ))}
        </div>
      </section>

      <section className="dashboard-main-grid">
        {chartData.length > 0 ? (
          <PriceLineChart
            data={chartData}
            title="Tracked Price History"
            subtitle={featuredItemName ? `${featuredItemName}` : ""}
          />
        ) : (
          <div className="chart-card">
            <div className="chart-header">
              <div>
                <div className="section-card-title">Tracked Price History</div>
                <div className="section-card-subtitle">
                  {featuredItemName
                    ? `${featuredItemName} does not have enough history yet.`
                    : "Price history will appear once tracked items accumulate snapshots."}
                </div>
              </div>
            </div>
            <div className="chart-wrap" style={{ display: "flex", alignItems: "center" }}>
              <p style={{ color: "#6b7280", margin: 0 }}>
                No historical trend is available to chart right now.
              </p>
            </div>
          </div>
        )}

        <div className="smart-alerts-card">
          <div className="section-card-title">Alert Summary</div>

          <div className="alerts-stack">
            {activeAlerts.length === 0 && !loading ? (
              <div className="smart-alert-item">
                <div className="smart-alert-body">
                  <div className="smart-alert-title">No alerts need attention</div>
                  <div className="smart-alert-desc">
                    Price-drop and delivery issues will appear here when the backend detects them.
                  </div>
                </div>
              </div>
            ) : (
              activeAlerts.slice(0, 3).map((alert) => (
                <div key={alert.id} className="smart-alert-item">
                  <div className="smart-alert-body">
                    <div className="smart-alert-title">{alert.title}</div>
                    <div className="smart-alert-desc">{alert.body}</div>
                    <Link className="secondary-btn full-width-btn" to="/alerts?tab=active">
                      Open Alerts
                    </Link>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </section>

      <section className="dashboard-main-grid">
        <div className="table-card">
          <div className="table-card-header">
            <div>
              <div className="section-card-title">Savings Summary</div>
              <div className="section-card-subtitle">
                Outcomes logged from alerts roll into your savings totals.
              </div>
            </div>
            <Link className="plain-link-btn" to="/savings">
              View Savings
            </Link>
          </div>

          <div className="summary-row">
            <span>Total actions</span>
            <strong>{savingsSummary.totalActions}</strong>
          </div>
          <div className="summary-row">
            <span>Successful actions</span>
            <strong>{savingsSummary.successfulActions}</strong>
          </div>
          <div className="summary-divider"></div>

          {savingsSummary.breakdown.length > 0 ? (
            savingsSummary.breakdown.map((entry) => (
              <div className="summary-row" key={entry.action_taken}>
                <span>{String(entry.action_taken).replaceAll("_", " ")}</span>
                <strong>{formatMoney(entry.total_recovered)}</strong>
              </div>
            ))
          ) : (
            <p style={{ color: "#6b7280", margin: 0 }}>
              No savings outcomes have been recorded yet.
            </p>
          )}
        </div>

        <div className="table-card">
          <div className="table-card-header">
            <div>
              <div className="section-card-title">Subscription Summary</div>
              <div className="section-card-subtitle">
                Track recurring charges and cancellation guidance in one place.
              </div>
            </div>
            <Link className="plain-link-btn" to="/subscriptions">
              View Subscriptions
            </Link>
          </div>

          {subscriptions.length === 0 ? (
            <p style={{ color: "#6b7280", margin: 0 }}>
              No recurring subscriptions have been detected yet.
            </p>
          ) : (
            <>
              <div className="summary-row">
                <span>Detected subscriptions</span>
                <strong>{subscriptions.length}</strong>
              </div>
              <div className="summary-row">
                <span>Upcoming charge</span>
                <strong>
                  {upcomingSubscription?.next_expected_charge
                    ? formatDate(upcomingSubscription.next_expected_charge)
                    : "Not available"}
                </strong>
              </div>
              <div className="summary-divider"></div>
              {subscriptions.slice(0, 3).map((subscription) => (
                <div className="summary-row" key={subscription.id}>
                  <span>{subscription.product_name}</span>
                  <strong>{subscription.retailer}</strong>
                </div>
              ))}
            </>
          )}
        </div>
      </section>

      <section className="section-block">
        <div className="section-label">Recent Purchases</div>

        <div className="table-card">
          <div className="table-card-header">
            <div>
              <div className="section-card-title">Recent Purchases</div>
            </div>
            <Link className="plain-link-btn" to="/orders">
              View All
            </Link>
          </div>

          <table className="data-table">
            <thead>
              <tr>
                <th>STORE</th>
                <th>PRODUCT</th>
                <th>PRICE</th>
                <th>STATUS</th>
                <th>DATE</th>
              </tr>
            </thead>
            <tbody>
              {recentPurchases.length === 0 && !loading ? (
                <tr>
                  <td colSpan="5">No orders found.</td>
                </tr>
              ) : (
                recentPurchases.map((row) => (
                  <tr key={row.id}>
                    <td>{row.store}</td>
                    <td>{row.product}</td>
                    <td className="strong-text">{row.price}</td>
                    <td>
                      <span className={`status-pill ${getStatusClass(row.status)}`}>
                        {row.status}
                      </span>
                    </td>
                    <td>{row.date}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
