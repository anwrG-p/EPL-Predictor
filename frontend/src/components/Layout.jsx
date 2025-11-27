import React from 'react';
import { Link, useNavigate } from 'react-router-dom';

export default function Layout({ children }) {
  const navigate = useNavigate();
  const isAdmin = localStorage.getItem('token') && (localStorage.getItem('userEmail') === 'anouarguemri1@gmail.com');

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('userEmail'); // Cleanup
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow p-4">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <Link to="/" className="text-2xl font-bold text-indigo-700">EPL Predictor</Link>
          <div className="flex space-x-4 items-center">
            <Link to="/" className="text-gray-600 hover:text-indigo-700">Prediction</Link>
            {/* Minimal simulation page - linking sim routes to admin for simplicity */}
            {isAdmin && <Link to="/admin" className="text-gray-600 hover:text-indigo-700 font-bold">Admin</Link>}
            <button onClick={handleLogout} className="bg-red-500 text-white px-3 py-1 rounded text-sm hover:bg-red-600 transition">Logout</button>
          </div>
        </div>
      </nav>
      <main className="py-8">
        {children}
      </main>
    </div>
  );
}
