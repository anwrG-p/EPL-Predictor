import React, { useState, useEffect } from 'react';
import { HashRouter as Router, Routes, Route, Link } from 'react-router-dom';
import axios from 'axios';
import Predictor from './components/Predictor.jsx';
import Login from './components/Login.jsx';
import Register from './components/Register.jsx';
import AdminPanel from './components/AdminPanel.jsx';
import './index.css';

// NOTE on API_URL: This must be your public backend URL.
// Ensure this matches the URL you set in AdminPanel.jsx and Login.jsx.
// For example: 'https://epl-predictor-api.com'
const API_URL = 'http://localhost:8000';

// Configure Axios defaults here to handle authentication and CORS
axios.defaults.baseURL = API_URL;
axios.defaults.withCredentials = true; // Important for handling cookies/CORS if needed

function App() {
  const [token, setToken] = useState(localStorage.getItem('token') || null);
  const [isAdmin, setIsAdmin] = useState(
    localStorage.getItem('isAdmin') === 'true'
  );

  // Effect to update local storage whenever token or isAdmin changes
  useEffect(() => {
    if (token) {
      localStorage.setItem('token', token);
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    } else {
      localStorage.removeItem('token');
      delete axios.defaults.headers.common['Authorization'];
    }
    localStorage.setItem('isAdmin', isAdmin);
  }, [token, isAdmin]);

  const handleLogout = () => {
    setToken(null);
    setIsAdmin(false);
  };

  return (
    <Router>
      <div className="min-h-screen bg-dark-bg text-dark-text font-sans selection:bg-primary-500/30">

        {/* Background Gradient Effects */}
        <div className="fixed inset-0 z-0 overflow-hidden pointer-events-none">
          <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-primary-600/20 rounded-full blur-[120px] animate-pulse"></div>
          <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] bg-purple-600/20 rounded-full blur-[120px] animate-pulse" style={{ animationDelay: '1s' }}></div>
        </div>

        {/* Navigation Bar */}
        <header className="fixed top-0 w-full z-50 glass border-b border-white/5">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center h-16">
              <Link to="/" className="flex items-center space-x-2 group">
                <span className="text-2xl transform group-hover:scale-110 transition-transform duration-300">⚽</span>
                <span className="text-xl font-display font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-primary-200">
                  EPL Predictor
                </span>
              </Link>

              <nav className="flex items-center space-x-8">
                {token ? (
                  <>
                    {isAdmin && (
                      <Link to="/admin" className="text-sm font-medium text-dark-muted hover:text-white transition-colors">
                        Admin Panel
                      </Link>
                    )}
                    <button
                      onClick={handleLogout}
                      className="text-sm font-medium text-red-400 hover:text-red-300 transition-colors"
                    >
                      Logout
                    </button>
                  </>
                ) : (
                  <div className="flex items-center space-x-4">
                    <Link to="/login" className="text-sm font-medium text-dark-muted hover:text-white transition-colors">
                      Login
                    </Link>
                    <Link to="/register" className="btn-primary text-sm">
                      Sign Up
                    </Link>
                  </div>
                )}
              </nav>
            </div>
          </div>
        </header>

        {/* Main Content Area */}
        <main className="relative z-10 pt-24 pb-12 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto">
          <div className="animate-fade-in">
            <Routes>
              {/* Home Route */}
              <Route path="/" element={<Predictor token={token} />} />

              {/* Login Route */}
              <Route path="/login" element={<Login setToken={setToken} setIsAdmin={setIsAdmin} />} />

              {/* Register Route */}
              <Route path="/register" element={<Register />} />

              {/* Admin Route (Protected) */}
              <Route path="/admin" element={<AdminPanel isAdmin={isAdmin} token={token} />} />

              {/* Fallback/404 Route */}
              <Route path="*" element={
                <div className="text-center py-20">
                  <h1 className="text-6xl font-display font-bold text-transparent bg-clip-text bg-gradient-to-r from-primary-400 to-purple-400 mb-4">404</h1>
                  <p className="text-dark-muted text-xl">Page not found</p>
                </div>
              } />
            </Routes>
          </div>
        </main>
      </div>
    </Router>
  );
}

export default App;
