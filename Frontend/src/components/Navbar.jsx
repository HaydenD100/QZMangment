import React from "react";
import { useNavigate } from "react-router-dom";
import "../App.css";

export default function Navbar({ role, username, onToggleView, view }) {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem("role");
    localStorage.removeItem("username");
    navigate("/login");
  };

  return (
    <nav className="navbar">
      <div className="navbar-brand">
        <span>QZManagement</span>
        {role === "admin" && (
          <button
            onClick={onToggleView}
            className="nav-button"
          >
            {view === "global" ? "Switch to Personal View" : "Switch to Global View"}
          </button>
        )}
      </div>

      <div className="navbar-user">
        <span>Logged in as: {username || role}</span>
        <button
          onClick={handleLogout}
          className="nav-button logout-button"
        >
          Logout
        </button>
      </div>
    </nav>
  );
}