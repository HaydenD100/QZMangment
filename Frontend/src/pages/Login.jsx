import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "../App.css";

export default function Login() {
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleLogin = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError("");

    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000));

    if (email === "admin@qz.com" && password === "admin123") {
      localStorage.setItem("role", "admin");
      localStorage.setItem("username", "Admin User");
      navigate("/admin");
    } else if (email === "user@qz.com" && password === "user123") {
      localStorage.setItem("role", "user");
      localStorage.setItem("username", "Regular User");
      navigate("/user");
    } else {
      setError("Invalid email or password");
    }
    
    setIsLoading(false);
  };

  return (
    <div className="login-container">
      <div className="login-card">
        {}
        <div className="login-header">
          <div className="login-logo">
            <svg fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M2.166 4.999A11.954 11.954 0 0010 1.944 11.954 11.954 0 0017.834 5c.11.65.166 1.32.166 2.001 0 5.225-3.34 9.67-8 11.317C5.34 16.67 2 12.225 2 7c0-.682.057-1.35.166-2.001zm11.541 3.708a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            </svg>
          </div>
          <h1 className="login-title">QZManagement</h1>
          <p className="login-subtitle">Software Security Scanner</p>
        </div>

        {}
        {error && (
          <div className="error-message">
            <div className="error-icon">
              <svg fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
              </svg>
            </div>
            <span>{error}</span>
          </div>
        )}

        {}
        <form onSubmit={handleLogin} className="login-form">
          <div className="form-group">
            <label className="form-label">Email Address</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="form-input"
              placeholder="Enter your email"
            />
          </div>

          <div className="form-group">
            <label className="form-label">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="form-input"
              placeholder="Enter your password"
            />
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="login-button"
          >
            {isLoading ? (
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}>
                <div className="loading-spinner"></div>
                Signing in...
              </div>
            ) : (
              "Sign In to Dashboard"
            )}
          </button>
        </form>

        {}
        <div className="demo-credentials">
          <h3 className="demo-title">
            <svg fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
            </svg>
            Demo Credentials
          </h3>
          <div className="credential-group">
            <span className="credential-label">Admin Access:</span>
            <div className="credential-values">
              <span className="credential-value credential-email">admin@qz.com</span>
              <span className="credential-value credential-password">admin123</span>
            </div>
          </div>
          <div className="credential-group">
            <span className="credential-label">User Access:</span>
            <div className="credential-values">
              <span className="credential-value credential-email">user@qz.com</span>
              <span className="credential-value credential-password">user123</span>
            </div>
          </div>
        </div>

        {}
        <div className="login-footer">
          <p className="footer-text">Secure software management for your organization</p>
        </div>
      </div>
    </div>
  );
}