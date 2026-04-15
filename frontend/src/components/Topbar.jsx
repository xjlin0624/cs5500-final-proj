import React, { useEffect, useState } from "react";
import { useLocation } from "react-router-dom";
import { getSelf } from "../api";

function getPageTitle(pathname) {
  if (pathname === "/dashboard") return "Overview";
  if (pathname === "/orders") return "My Orders";
  if (pathname === "/alerts") return "Price Alerts";
  if (pathname === "/savings") return "Savings Tool";
  if (pathname === "/subscriptions") return "Subscriptions";
  if (pathname === "/settings") return "Settings";
  return "Overview";
}

export default function Topbar({ onLogout }) {
  const location = useLocation();
  const pageTitle = getPageTitle(location.pathname);
  const [user, setUser] = useState(null);

  useEffect(() => {
    getSelf().then(setUser).catch(() => {});
  }, []);

  return (
    <header className="topbar">
      <div className="topbar-title">{pageTitle}</div>

      <div className="topbar-right">
        <div className="search-wrap">
          <span className="search-icon">⌕</span>
          <input
            className="search-input"
            placeholder="Search orders or stores..."
          />
        </div>

        <div className="profile-wrap">
          <div className="profile-text">
            <div className="profile-name">{user?.display_name || user?.email || "Account"}</div>
            <div className="profile-sub">{user?.email || ""}</div>
          </div>
          <div className="profile-avatar">⍟</div>
          {onLogout && (
            <button className="plain-link-btn" onClick={onLogout} style={{ marginLeft: "8px" }}>
              Sign out
            </button>
          )}
        </div>
      </div>
    </header>
  );
}