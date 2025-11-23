import React from "react";
import { useParams, useNavigate } from "react-router-dom";
import Navbar from "../components/Navbar";
import "../App.css";

// Mock data
const mockSoftwareData = {
  "Node.js": {
    Name: "Node.js",
    Version: "18.17.0",
    Status: "Update Available",
    RiskLevel: "Critical",
    Recommendation: "Update to version 20.x immediately",
    users: [
      { userId: "john.doe", version: "14.15.0", status: "Outdated", riskLevel: "Critical" },
      { userId: "jane.smith", version: "18.17.0", status: "Supported", riskLevel: "OK" },
      { userId: "mike.johnson", version: "16.20.0", status: "Update Available", riskLevel: "High" },
      { userId: "sarah.wilson", version: "12.18.0", status: "Outdated", riskLevel: "Critical" },
      { userId: "alex.brown", version: "14.15.0", status: "Outdated", riskLevel: "Critical" }
    ]
  },
  "Chrome": {
    Name: "Chrome",
    Version: "119.0",
    Status: "Supported",
    RiskLevel: "Informational",
    Recommendation: "Latest version installed",
    users: [
      { userId: "john.doe", 
        version: "119.0", 
        status: "Supported", 
        riskLevel: "OK" },

      { userId: "jane.smith", 
        version: "118.0", 
        status: "Update Available", 
        riskLevel: "Informational" },

      { userId: "mike.johnson", 
        version: "115.0", 
        status: "Outdated", 
        riskLevel: "Medium" }
    ]
  },
  "VS Code": {
    Name: "VS Code",
    Version: "1.84.0",
    Status: "Supported",
    RiskLevel: "OK",
    Recommendation: "Up to date",
    users: [
      { userId: "john.doe", 
        version: "1.84.0", 
        status: "Supported", 
        riskLevel: "OK" },

      { userId: "jane.smith", 
        version: "1.84.0", 
        status: "Supported", 
        riskLevel: "OK" },

      { userId: "mike.johnson", 
        version: "1.84.0", 
        status: "Supported", 
        riskLevel: "OK" }
    ]
  },
  "Adobe Reader": {
    Name: "Adobe Reader",
    Version: "2023.006.20320",
    Status: "Outdated",
    RiskLevel: "High",
    Recommendation: "Security update required",
    users: [
      { userId: "john.doe", 
        version: "2022.001.20085", 
        status: "Outdated", 
        riskLevel: "High" },

      { userId: "jane.smith", 
        version: "2023.006.20320", 
        status: "Supported", 
        riskLevel: "OK" },

      { userId: "mike.johnson", 
        version: "2020.001.20085", 
        status: "Outdated", 
        riskLevel: "Critical" }
    ]
  },
  "Python": {
    Name: "Python",
    Version: "3.11.0",
    Status: "Update Available",
    RiskLevel: "Medium",
    Recommendation: "Consider updating to 3.12.0",
    users: [
      { userId: "john.doe", 
        version: "3.9.0", 
        status: "Outdated", 
        riskLevel: "Medium" },

      { userId: "jane.smith", 
        version: "3.11.0", 
        status: "Supported", 
        riskLevel: "OK" },

      { userId: "mike.johnson", 
        version: "3.8.0", 
        status: "Outdated", 
        riskLevel: "High" }
    ]
  }
};

// Risk level sorting order
const riskLevelOrder = {
  "Critical": 1,
  "High": 2,
  "Medium": 3,
  "Low": 4,
  "Informational": 5,
  "OK": 6
};

export default function SoftwareDetail() {
  const { softwareName } = useParams();
  const navigate = useNavigate();
  
  const software = mockSoftwareData[softwareName];

  if (!software) {
    return (
      <div className="dashboard-container">
        <Navbar role="admin" username="Admin User" />
        <div className="dashboard-content">
          <div className="error-state">
            <h2>Software Not Found</h2>
            <p>The software "{softwareName}" could not be found.</p>
            <button onClick={() => navigate("/admin")} className="action-button primary-button">
              Return to Dashboard
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Filter users to only show those with issues (not OK)
  const usersWithIssues = software.users
    .filter(user => user.riskLevel !== "OK")
    .sort((a, b) => riskLevelOrder[a.riskLevel] - riskLevelOrder[b.riskLevel]);

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

  return (
    <div className="dashboard-container">
      <Navbar role="admin" username="Admin User" />

      <div className="dashboard-content">
        <div className="dashboard-header">
          <div>
            <button 
              onClick={() => navigate("/admin")}
              className="back-button"
            >
              ← Back to Dashboard
            </button>
            <h1 className="dashboard-title">{software.Name}</h1>
            <p className="dashboard-subtitle">
              Version {software.Version} • {software.Status} • {software.RiskLevel} Risk
            </p>
          </div>
          <div className="software-risk-indicator">
            <span className={getRiskBadgeClass(software.RiskLevel)}>
              {software.RiskLevel} Risk
            </span>
          </div>
        </div>

        {/* Software Overview */}
        <div className="software-overview">
          <div className="overview-card">
            <h3>Recommendation</h3>
            <p>{software.Recommendation}</p>
          </div>
          <div className="overview-card">
            <h3>Affected Users</h3>
            <p>{usersWithIssues.length} user{usersWithIssues.length !== 1 ? 's' : ''} with issues</p>
          </div>
        </div>

        {/* Users Table */}
        <div className="table-container">
          <div className="table-header">
            <h2>Affected Users</h2>
            <p className="table-subtitle">
              {usersWithIssues.length > 0 
                ? `Showing ${usersWithIssues.length} user${usersWithIssues.length !== 1 ? 's' : ''} with security issues`
                : 'No users with security issues'
              }
            </p>
          </div>
          
          {usersWithIssues.length > 0 ? (
            <div className="table-scroll">
              <table className="data-table">
                <thead>
                  <tr>
                    <th>User</th>
                    <th>Version</th>
                    <th>Status</th>
                    <th>Risk Level</th>
                  </tr>
                </thead>
                <tbody>
                  {usersWithIssues.map((user, index) => (
                    <tr key={index}>
                      <td className="user-id">{user.userId}</td>
                      <td>{user.version}</td>
                      <td><span className={getStatusClass(user.status)}>{user.status}</span></td>
                      <td><span className={getRiskBadgeClass(user.riskLevel)}>{user.riskLevel}</span></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="no-issues-message">
              <div className="no-issues-icon">✅</div>
              <h3>No Security Issues Detected</h3>
              <p>All users have the latest, secure version of {software.Name} installed.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}