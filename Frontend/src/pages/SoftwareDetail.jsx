import React from "react";
import { useParams, useNavigate } from "react-router-dom";
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

export default function SoftwareDetail() {
  const { softwareName } = useParams();
  const navigate = useNavigate();
  console.log(softwareName)

      useEffect(() => {
  const fetchSoftware = async () => {
    try {
      const response = await fetch("http://127.0.0.1:5000/GetSoftwareByName", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          username: localStorage.getItem("username"),
          password: localStorage.getItem("password"),
          softwareName: softwareName
        })
      });

      const data = await response.json();
      console.log(data);

      const sortedSoftware = [...data].sort(
          (a, b) => riskLevelOrder[a.RiskLevel] - riskLevelOrder[b.RiskLevel]
        );

        setSoftware(sortedSoftware);
        console.log(sortedSoftware)

    } catch (error) {
      console.error("Error fetching software:", error);
    }
  };

  fetchSoftware();
}, []); // empty dependency array

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