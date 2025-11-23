import React, { useEffect, useState } from 'react';
import Navbar from "../components/Navbar";
import "../App.css";

const mockUserSoftware = [
  {
    Name: "Chrome",
    Version: "114.0",
    SupportStatus: "Supported",
    RiskLevel: "Low",
    LastScanned: "2024-01-15",
  },
  {
    Name: "Node.js",
    Version: "14.15.0",
    SupportStatus: "Outdated",
    RiskLevel: "High",
    LastScanned: "2024-01-15",
  },
  {
    Name: "VS Code",
    Version: "1.78",
    SupportStatus: "Supported",
    RiskLevel: "Low",
    LastScanned: "2024-01-15",
  },
  {
    Name: "Adobe Reader",
    Version: "2022.001.20085",
    SupportStatus: "Update Available",
    RiskLevel: "Medium",
    LastScanned: "2024-01-15",
  },
];

export default function UserDashboard() {
  const [software, setSoftware] = useState([]);
  const [loading, setLoading] = useState(false);
  const [scanProgress, setScanProgress] = useState(0);

  useEffect(() => {
    setTimeout(() => {
      setSoftware(mockUserSoftware);
    }, 500);
  }, []);

  const handleScan = async () => {
    setLoading(true);
    setScanProgress(0);
    
    const interval = setInterval(() => {
      setScanProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval);
          return 100;
        }
        return prev + 10;
      });
    }, 200);

    await new Promise(resolve => setTimeout(resolve, 2000));
    clearInterval(interval);
    
    const updated = [...mockUserSoftware];
    updated[1] = { ...updated[1], Version: "18.17.0", SupportStatus: "Supported", RiskLevel: "Low" };
    setSoftware(updated);
    setLoading(false);
    setScanProgress(0);
  };

  const getRiskBadgeClass = (risk) => {
    switch (risk) {
      case 'Low': return 'badge badge-success';
      case 'Medium': return 'badge badge-warning';
      case 'High': return 'badge badge-critical';
      default: return 'badge badge-info';
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

  const stats = {
    total: software.length,
    highRisk: software.filter(s => s.RiskLevel === "High").length,
    needsUpdate: software.filter(s => s.SupportStatus === "Update Available" || s.SupportStatus === "Outdated").length,
  };

  return (
    <div className="dashboard-container">
      <Navbar role="user" username="Regular User" />
      
      <div className="dashboard-content">
        <div className="dashboard-header">
          <div>
            <h1 className="dashboard-title">User Dashboard</h1>
            <p className="dashboard-subtitle">Monitor your software security status</p>
          </div>
          
          <button
            onClick={handleScan}
            disabled={loading}
            className="action-button primary-button"
          >
            {loading ? "Scanning..." : "Scan Now"}
          </button>
        </div>

        {/* Scan Progress */}
        {loading && (
          <div className="scan-progress">
            <div className="progress-header">
              <span>Scanning your system...</span>
              <span>{scanProgress}%</span>
            </div>
            <div className="progress-bar">
              <div 
                className="progress-fill"
                style={{ width: `${scanProgress}%` }}
              ></div>
            </div>
          </div>
        )}

        {/* Stats Cards */}
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-value">{stats.total}</div>
            <div className="stat-label">Total Software</div>
          </div>
          <div className="stat-card">
            <div className="stat-value stat-critical">{stats.highRisk}</div>
            <div className="stat-label">High Risk Items</div>
          </div>
          <div className="stat-card">
            <div className="stat-value stat-warning">{stats.needsUpdate}</div>
            <div className="stat-label">Needs Update</div>
          </div>
        </div>

        {/* Software Table */}
        <div className="table-container">
          <div className="table-header">
            <h2>Your Software</h2>
          </div>
          <div className="table-scroll">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Software</th>
                  <th>Version</th>
                  <th>Status</th>
                  <th>Risk Level</th>
                </tr>
              </thead>
              <tbody>
                {software.map((item, idx) => (
                  <tr key={idx}>
                    <td>{item.Name}</td>
                    <td>{item.Version}</td>
                    <td><span className={getStatusClass(item.SupportStatus)}>{item.SupportStatus}</span></td>
                    <td><span className={getRiskBadgeClass(item.RiskLevel)}>{item.RiskLevel}</span></td>
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