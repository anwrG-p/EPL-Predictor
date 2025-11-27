import React, { useState, useEffect } from 'react';
import { HashRouter as Router, Routes, Route, Link } from 'react-router-dom';
import axios from 'axios';
import Predictor from './components/Predictor.jsx';
import Login from './components/Login.jsx';
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
      <div className="min-h-screen bg-gray-900 text-white font-sans">
        
        {/* Navigation Bar */}
        <header className="bg-gray-800 shadow-md p-4">
          <div className="flex justify-between items-center max-w-7xl mx-auto">
            <Link to="/" className="text-2xl font-bold text-indigo-400 hover:text-indigo-300 transition duration-300">
              ⚽ EPL Predictor
            </Link>
            
            <nav className="flex space-x-6 items-center">
              {token ? (
                <>
                  {isAdmin && (
                    <Link to="/admin" className="text-gray-300 hover:text-indigo-400 transition">
                      Admin Panel
                    </Link>
                  )}
                  <button 
                    onClick={handleLogout} 
                    className="px-4 py-2 text-sm font-medium text-white bg-red-600 rounded-md hover:bg-red-700 transition"
                  >
                    Logout
                  </button>
                </>
              ) : (
                <Link to="/login" className="px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-md hover:bg-indigo-700 transition">
                  Login
                </Link>
              )}
            </nav>
          </div>
        </header>

        {/* Main Content Area */}
        <main className="py-10">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <Routes>
              {/* Home Route */}
              <Route path="/" element={<Predictor token={token} />} />
              
              {/* Login Route */}
              <Route path="/login" element={<Login setToken={setToken} setIsAdmin={setIsAdmin} />} />
              
              {/* Admin Route (Protected) */}
              <Route path="/admin" element={<AdminPanel isAdmin={isAdmin} token={token} />} />
              
              {/* Fallback/404 Route */}
              <Route path="*" element={<h1 className="text-red-400 text-4xl text-center">404 - Page Not Found</h1>} />
            </Routes>
          </div>
        </main>
      </div>
    </Router>
  );
}

export default App;
