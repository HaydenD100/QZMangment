import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import Navbar from "../components/Navbar";
import "../App.css";

const mockSoftwareData = [
  {
    id: 1,
    Name: "Node.js",
    Version: "18.17.0",
    Status: "Update Available",
    RiskLevel: "Critical",
    Recommendation: "Update to version 20.x immediately",
    users: [
      { userId: "user1",
        version: "14.15.0",
        status: "Outdated",
        riskLevel: "Critical" },

      { userId: "user2", 
        version: "18.17.0", 
        status: "Supported", 
        riskLevel: "OK" },

      { userId: "user3", 
        version: "16.20.0", 
        status: "Update Available", 
        riskLevel: "High" },

      { userId: "user4", 
        version: "12.18.0", 
        status: "Outdated", 
        riskLevel: "Critical" }
    ]
  },
  {
    id: 2,
    Name: "Chrome",
    Version: "119.0",
    Status: "Supported",
    RiskLevel: "Informational",
    Recommendation: "Latest version installed",
    users: [
      { userId: "user1", 
        version: "119.0", 
        status: "Supported", 
        riskLevel: "OK" },

      { userId: "user2", 
        version: "118.0", 
        status: "Update Available", 
        riskLevel: "Informational" },

      { userId: "user3", 
        version: "115.0", 
        status: "Outdated", 
        riskLevel: "Medium" }
    ]
  },
  {
    id: 3,
    Name: "VS Code",
    Version: "1.84.0",
    Status: "Supported",
    RiskLevel: "OK",
    Recommendation: "Up to date",
    users: [
      { userId: "user1", 
        version: "1.84.0", 
        status: "Supported", 
        riskLevel: "OK" },

      { userId: "user2", 
        version: "1.84.0", 
        status: "Supported", 
        riskLevel: "OK" },

      { userId: "user3", 
        version: "1.84.0", 
        status: "Supported", 
        riskLevel: "OK" }
    ]
  },
  {
    id: 4,
    Name: "Adobe Reader",
    Version: "2023.006.20320",
    Status: "Outdated",
    RiskLevel: "High",
    Recommendation: "Security update required",
    users: [
      { userId: "user1", 
        version: "2022.001.20085", 
        status: "Outdated", 
        riskLevel: "High" },

      { userId: "user2", 
        version: "2023.006.20320", 
        status: "Supported", 
        riskLevel: "OK" },

      { userId: "user3", 
        version: "2020.001.20085", 
        status: "Outdated", 
        riskLevel: "Critical" }
    ]
  },
  {
    id: 5,
    Name: "Python",
    Version: "3.11.0",
    Status: "Update Available",
    RiskLevel: "Medium",
    Recommendation: "Consider updating to 3.12.0",
    users: [
      { userId: "user1", 
        version: "3.9.0", 
        status: "Outdated", 
        riskLevel: "Medium" },

      { userId: "user2", 
        version: "3.11.0", 
        status: "Supported", 
        riskLevel: "OK" },
        
      { userId: "user3",
        version: "3.8.0", 
        status: "Outdated",
        riskLevel: "High" }
    ]
  }
];

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
    // Sort software by risk level (Critical -> High -> Medium -> Low -> Informational -> OK)
    const sortedSoftware = [...mockSoftwareData].sort((a, b) => {
      return riskLevelOrder[a.RiskLevel] - riskLevelOrder[b.RiskLevel];
    });
    setSoftware(sortedSoftware);
  }, []);

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
                  <th>Risk Level</th>
                  <th>Recommendation</th>
                </tr>
              </thead>
              <tbody>
                {filteredSoftware.map((item) => (
                  <tr key={item.id}>
                    <td>
                      <button 
                        className="software-link"
                        onClick={() => handleSoftwareClick(item.Name)}
                      >
                        {item.Name}
                      </button>
                    </td>
                    <td>{item.Version}</td>
                    <td><span className={getStatusClass(item.Status)}>{item.Status}</span></td>
                    <td><span className={getRiskBadgeClass(item.RiskLevel)}>{item.RiskLevel}</span></td>
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