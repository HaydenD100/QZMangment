import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import Navbar from "../components/Navbar";
import "../App.css";

// Risk level sorting order
const riskLevelOrder = {
  "Critical": 1,
  "High": 2,
  "Medium": 3,
  "Low": 4,
  "Informational": 5,
  "OK": 6
};

export default function AdminDashboard() {
  const navigate = useNavigate();
  const [software, setSoftware] = useState([]);
  const [view, setView] = useState("global");

    useEffect(() => {
  const fetchSoftware = async () => {
    try {
      const response = await fetch("http://127.0.0.1:5000/GetUserSoftware", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          username: localStorage.getItem("username"),
          password: localStorage.getItem("password")
        })
      });

      const data = await response.json();
      console.log(data);

      // Sort software by risk level
      const sortedSoftware = [...data].sort((a, b) => {
        return riskLevelOrder[a.RiskLevel] - riskLevelOrder[b.RiskLevel];
      });

      setSoftware(sortedSoftware);

    } catch (error) {
      console.error("Error fetching software:", error);
    }
  };

  fetchSoftware();
}, []); // empty dependency array


  const handleSoftwareClick = (softwareName) => {
    navigate(`/software/${encodeURIComponent(softwareName)}`);
  };

  const getRiskBadgeClass = (risk) => {
    switch (risk) {
      case "OK": return "badge badge-success";
      case "Informational": return "badge badge-info";
      case "Low": return "badge badge-low";
      case "Medium": return "badge badge-warning";
      case "High": return "badge badge-high";
      case "Critical": return "badge badge-critical";
      default: return "badge badge-info";
    }
  };

  const getStatusClass = (status) => {
    switch (status) {
      case "Supported": return "badge badge-success";
      case "Outdated": return "badge badge-critical";
      case "Update Available": return "badge badge-warning";
      default: return "badge badge-info";
    }
  };

  const filteredSoftware = view === "global" ? software : software.filter((s) => 
    s.users.some(user => user.userId === "admin")
  );

  const stats = {
    total: filteredSoftware.length,
    critical: filteredSoftware.filter(s => s.RiskLevel === "Critical").length,
    high: filteredSoftware.filter(s => s.RiskLevel === "High").length,
    medium: filteredSoftware.filter(s => s.RiskLevel === "Medium").length,
  };

  return (
    <div className="dashboard-container">
      <Navbar
        role="admin"
        username="Admin User"
        view={view}
        onToggleView={() => setView(view === "global" ? "personal" : "global")}
      />

      <div className="dashboard-content">
        <div className="dashboard-header">
          <div>
            <h1 className="dashboard-title">Admin Dashboard</h1>
            <p className="dashboard-subtitle">
              {view === "global" ? "Global view of all company software" : "Your personal software"}
            </p>
          </div>
          <div className="header-actions">
            <button
              onClick={() => setView(view === "global" ? "personal" : "global")}
              className="action-button secondary-button"
            >
              Switch to {view === "global" ? "Personal" : "Global"} View
            </button>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-value">{stats.total}</div>
            <div className="stat-label">Total Software</div>
          </div>
          <div className="stat-card">
            <div className="stat-value stat-critical">{stats.critical}</div>
            <div className="stat-label">Critical Risks</div>
          </div>
          <div className="stat-card">
            <div className="stat-value stat-high">{stats.high}</div>
            <div className="stat-label">High Risks</div>
          </div>
          <div className="stat-card">
            <div className="stat-value stat-warning">{stats.medium}</div>
            <div className="stat-label">Medium Risks</div>
          </div>
        </div>

        {/* Software Table */}
        <div className="table-container">
          <div className="table-header">
            <h2>Software Inventory</h2>
            <p className="table-subtitle">Click on software names to view affected users</p>
          </div>
          <div className="table-scroll">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Software</th>
                  <th>Version</th>
                  <th>Status</th>
                  <th>LastScan</th>
                </tr>
              </thead>
              <tbody>
                {filteredSoftware.map((item) => (
                  <tr key={item.id}>
                    <td>
                      <button 
                        className="software-link"
                        onClick={() => handleSoftwareClick(item.ID)}
                      >
                        {item.Name}
                      </button>
                    </td>
                    <td>{item.Version}</td>
                    <td><span className={getStatusClass(item.Status)}>{item.Status}</span></td>
                    <td>{item.LastScan}</td>
                    <td>{item.Recommendation}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}