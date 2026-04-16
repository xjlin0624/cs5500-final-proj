import React, { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";

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
  const navigate = useNavigate();
  const pageTitle = getPageTitle(location.pathname);
  const [user, setUser] = useState(null);
  const [query, setQuery] = useState("");

  useEffect(() => {
    getSelf().then(setUser).catch(() => {});
  }, []);

  useEffect(() => {
    const params = new window.URLSearchParams(location.search);
    setQuery(params.get("q") || "");
  }, [location.search]);

  function handleSubmit(event) {
    event.preventDefault();
    const trimmed = query.trim();
    const params = new window.URLSearchParams();
    if (trimmed) {
      params.set("q", trimmed);
    }
    navigate(`/orders${params.toString() ? `?${params.toString()}` : ""}`);
  }

  return (
    <header className="topbar">
      <div className="topbar-title">{pageTitle}</div>

      <div className="topbar-right">
        <form className="search-wrap" onSubmit={handleSubmit}>
          <span className="search-icon">⌕</span>
          <input
            className="search-input"
            placeholder="Search orders or stores..."
            value={query}
            onChange={(event) => setQuery(event.target.value)}
          />
        </form>

        <div className="profile-wrap">
          <div className="profile-text">
            <div className="profile-name">{user?.display_name || user?.email || "Account"}</div>
            <div className="profile-sub">{user?.email || ""}</div>
          </div>
          <div className="profile-avatar">⌟</div>
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
