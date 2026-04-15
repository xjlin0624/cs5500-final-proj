import React, { useEffect, useState } from "react";

import { getPreferences, getSelf, registerPushToken, unregisterPushToken, updatePreferences } from "../api";
import { disableBrowserPush, enableBrowserPush, getStoredPushToken } from "../services/pushNotifications";

const defaultPreferences = {
  min_savings_threshold: 10,
  notify_price_drop: true,
  notify_delivery_anomaly: true,
  push_notifications_enabled: false,
  preferred_message_tone: "polite",
};

export default function Settings() {
  const [preferences, setPreferences] = useState(defaultPreferences);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [statusMessage, setStatusMessage] = useState("");
  const [errorMessage, setErrorMessage] = useState("");

  useEffect(() => {
    getSelf().then(setUser).catch(() => {});
  }, []);

  useEffect(() => {
    async function loadPreferences() {
      try {
        const data = await getPreferences();
        setPreferences({
          min_savings_threshold: data.min_savings_threshold,
          notify_price_drop: data.notify_price_drop,
          notify_delivery_anomaly: data.notify_delivery_anomaly,
          push_notifications_enabled: data.push_notifications_enabled,
          preferred_message_tone: data.preferred_message_tone,
        });
      } catch (error) {
        setErrorMessage(error.message || "Failed to load preferences.");
      } finally {
        setLoading(false);
      }
    }

    loadPreferences();
  }, []);

  function updateField(field, value) {
    setPreferences((current) => ({
      ...current,
      [field]: value,
    }));
  }

  async function handleSavePreferences() {
    setSaving(true);
    setStatusMessage("");
    setErrorMessage("");
    try {
      const updated = await updatePreferences(preferences);
      setPreferences({
        min_savings_threshold: updated.min_savings_threshold,
        notify_price_drop: updated.notify_price_drop,
        notify_delivery_anomaly: updated.notify_delivery_anomaly,
        push_notifications_enabled: updated.push_notifications_enabled,
        preferred_message_tone: updated.preferred_message_tone,
      });
      setStatusMessage("Preferences saved.");
    } catch (error) {
      setErrorMessage(error.message || "Failed to save preferences.");
    } finally {
      setSaving(false);
    }
  }

  async function handleEnablePush() {
    setSaving(true);
    setStatusMessage("");
    setErrorMessage("");

    try {
      const result = await enableBrowserPush();
      if (result.status !== "enabled") {
        throw new Error(result.reason || "Browser push is unavailable.");
      }

      await registerPushToken({
        token: result.token,
        platform: result.platform,
        browser: result.browser,
      });

      const updated = await updatePreferences({
        push_notifications_enabled: true,
      });
      updateField("push_notifications_enabled", updated.push_notifications_enabled);
      setStatusMessage("Browser push notifications enabled.");
    } catch (error) {
      setErrorMessage(error.message || "Failed to enable browser push.");
    } finally {
      setSaving(false);
    }
  }

  async function handleDisablePush() {
    setSaving(true);
    setStatusMessage("");
    setErrorMessage("");

    try {
      await disableBrowserPush(unregisterPushToken);
      const fallbackToken = getStoredPushToken();
      if (fallbackToken) {
        await unregisterPushToken(fallbackToken);
      }
      const updated = await updatePreferences({
        push_notifications_enabled: false,
      });
      updateField("push_notifications_enabled", updated.push_notifications_enabled);
      setStatusMessage("Browser push notifications disabled.");
    } catch (error) {
      setErrorMessage(error.message || "Failed to disable browser push.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="page-content">
      <div className="settings-tabs">
        <button className="pill-tab active">Account</button>
        <button className="pill-tab active">Notifications</button>
        <button className="pill-tab active">Preferences</button>
      </div>

      {loading && <p>Loading settings...</p>}
      {statusMessage && <p style={{ color: "green" }}>{statusMessage}</p>}
      {errorMessage && <p style={{ color: "red" }}>{errorMessage}</p>}

      <div className="settings-card">
        <div className="section-card-title">Account Information</div>

        <div className="settings-grid two-col">
          <div className="form-group">
            <label>First Name</label>
            <input value={user?.display_name || ""} readOnly />
          </div>

          <div className="form-group">
            <label>Last Name</label>
            <input value="" readOnly />
          </div>
        </div>

        <div className="settings-grid one-col">
          <div className="form-group">
            <label>Email</label>
            <input value={user?.email || ""} readOnly />
          </div>
        </div>

        <div className="settings-divider"></div>

        <div className="section-card-title">Notifications</div>

        <div className="settings-grid one-col">
          <label className="form-group">
            <span>Price drop alerts</span>
            <input
              type="checkbox"
              checked={preferences.notify_price_drop}
              onChange={(event) => updateField("notify_price_drop", event.target.checked)}
            />
          </label>
          <label className="form-group">
            <span>Delivery anomaly alerts</span>
            <input
              type="checkbox"
              checked={preferences.notify_delivery_anomaly}
              onChange={(event) => updateField("notify_delivery_anomaly", event.target.checked)}
            />
          </label>
          <div className="form-group">
            <label>Browser push</label>
            <div className="settings-actions">
              <button
                className="primary-btn"
                type="button"
                disabled={saving}
                onClick={handleEnablePush}
              >
                Enable Browser Push
              </button>
              <button
                className="secondary-btn"
                type="button"
                disabled={saving}
                onClick={handleDisablePush}
              >
                Disable Browser Push
              </button>
            </div>
          </div>
        </div>

        <div className="settings-divider"></div>

        <div className="section-card-title">Recommendation Preferences</div>

        <div className="settings-grid two-col">
          <div className="form-group">
            <label>Minimum Savings Threshold</label>
            <input
              type="number"
              min="0"
              step="1"
              value={preferences.min_savings_threshold}
              onChange={(event) =>
                updateField("min_savings_threshold", Number(event.target.value))
              }
            />
          </div>

          <div className="form-group">
            <label>Default Message Tone</label>
            <select
              value={preferences.preferred_message_tone}
              onChange={(event) =>
                updateField("preferred_message_tone", event.target.value)
              }
            >
              <option value="polite">Polite</option>
              <option value="firm">Firm</option>
              <option value="concise">Concise</option>
            </select>
          </div>
        </div>

        <div className="settings-actions">
          <button className="primary-btn" type="button" disabled={saving} onClick={handleSavePreferences}>
            {saving ? "Saving..." : "Save Preferences"}
          </button>
        </div>
      </div>
    </div>
  );
}
