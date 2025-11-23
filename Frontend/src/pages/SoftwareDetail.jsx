import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import Navbar from "../components/Navbar";
import "../App.css";

// Risk badge classes
const getRiskBadgeClass = (risk) => {
  switch (risk) {
    case "OK":
      return "badge badge-success";
    case "Informational":
      return "badge badge-info";
    case "Low":
      return "badge badge-low";
    case "Medium":
      return "badge badge-warning";
    case "High":
      return "badge badge-high";
    case "Critical":
      return "badge badge-critical";
    default:
      return "badge badge-info";
  }
};

export default function SoftwareDetail() {
  const { softwareName } = useParams();
  const navigate = useNavigate();
  const [software, setSoftware] = useState(null);

  useEffect(() => {
    const fetchSoftware = async () => {
      try {
        const response = await fetch("http://127.0.0.1:5000/GetSoftwareByName", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            username: localStorage.getItem("username"),
            password: localStorage.getItem("password"),
            softwareName: softwareName,
          }),
        });

        const data = await response.json();
        console.log("Fetched software:", data);
        setSoftware(data);
      } catch (error) {
        console.error("Error fetching software:", error);
      }
    };

    fetchSoftware();
  }, [softwareName]);

  if (!software) {
    return (
      <div className="dashboard-container">
        <Navbar role="admin" username="Admin User" />
        <div className="dashboard-content">
          <div className="error-state">
            <h2>Software Not Found</h2>
            <p>The software "{softwareName}" could not be found.</p>
            <button
              onClick={() => navigate("/admin")}
              className="action-button primary-button"
            >
              Return to Dashboard
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      <Navbar role="admin" username="Admin User" />

      <div className="dashboard-content">
        {/* Header */}
        <div className="dashboard-header">
          <div>
            <button onClick={() => navigate("/admin")} className="back-button">
              ← Back to Dashboard
            </button>
            <h1 className="dashboard-title">{software.Name}</h1>
            <p className="dashboard-subtitle">
              Version {software.Version} • {software.Status || "Supported"} •{" "}
              {software.RiskLevel || "OK"} Risk
            </p>
          </div>
          <div className="software-risk-indicator">
            <span className={getRiskBadgeClass(software.RiskLevel)}>
              {software.RiskLevel || "OK"} Risk
            </span>
          </div>
        </div>

        {/* Software Overview */}
        <div className="software-overview">
          <div className="overview-card">
  <h3>Risk Analysis</h3>
  {software.Summary ? (
    <ul className="vuln-list">
      {software.Summary.split("...").map((item, index) => {
        const match = item.match(/\[CVE-(\d{4}-\d+)\s*\|\s*Score:\s*([\d.]+)\]/);
        const description = item.replace(/\[CVE-\d{4}-\d+\s*\|\s*Score:\s*[\d.]+\]/, '').trim();
        return match ? (
          <li key={index}>
            <strong>{match[0]}</strong>: {description || "No description available."}
          </li>
        ) : null;
      })}
    </ul>
  ) : (
    <p>No recommendations available.</p>
  )}
</div>

        </div>
      </div>
    </div>
  );
}
