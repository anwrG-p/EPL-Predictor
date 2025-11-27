import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { settings } from '../../vite.config'; // Dummy import to show reliance on config/env

export default function AdminPanel() {
  const [stats, setStats] = useState(null);
  const [seasonSim, setSeasonSim] = useState([]);
  const [loading, setLoading] = useState(false);
  const [retrainStatus, setRetrainStatus] = useState('');
  
  const token = localStorage.getItem('token');
  const API_URL = 'http://localhost:8000';

  useEffect(() => {
    fetchStats();
    fetchSeasonSim();
  }, []);

  const fetchStats = async () => {
    try {
      const res = await axios.get(`${API_URL}/admin/stats`, { headers: { Authorization: `Bearer ${token}` } });
      setStats(res.data);
    } catch (err) {
      console.error("Failed to fetch admin stats:", err);
    }
  };

  const fetchSeasonSim = async () => {
    setLoading(true);
    try {
      const res = await axios.get(`${API_URL}/simulate-season?rounds=500`, { headers: { Authorization: `Bearer ${token}` } });
      setSeasonSim(res.data);
    } catch (err) {
      console.error("Failed to fetch season simulation:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleRetrain = async () => {
    setRetrainStatus('Training...');
    try {
      const res = await axios.post(`${API_URL}/admin/retrain`, {}, { headers: { Authorization: `Bearer ${token}` } });
      setRetrainStatus(`Success: ${res.data.metrics.status}. Reloading new model.`);
    } catch (err) {
      setRetrainStatus('Failed to retrain model. Check backend logs.');
      console.error(err);
    }
  };

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <h1 className="text-3xl font-bold mb-6 text-gray-800">📊 Admin Dashboard</h1>
      
      {/* Configuration & Controls */}
      <div className="bg-white p-6 shadow rounded mb-8 flex justify-between items-center">
        <div>
          <h2 className="text-xl font-semibold mb-2">Model Management</h2>
          <p>Current Model Type: <span className="font-mono text-indigo-600">{settings.VITE_MODEL_TYPE || 'ensemble'}</span> (Set via ENV)</p>
        </div>
        <button onClick={handleRetrain} className="bg-red-600 text-white px-6 py-2 rounded hover:bg-red-700 transition disabled:opacity-50" disabled={retrainStatus === 'Training...'}>
          {retrainStatus || 'Trigger Full Retrain'}
        </button>
      </div>

      {/* Stats */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-blue-50 p-6 rounded shadow">
            <p className="text-sm text-blue-600">Total Predictions</p>
            <p className="text-3xl font-extrabold">{stats.total_predictions}</p>
          </div>
          <div className="bg-blue-50 p-6 rounded shadow">
            <p className="text-sm text-blue-600">Last Retrain</p>
            <p className="text-3xl font-extrabold">N/A (See logs)</p>
          </div>
          <div className="bg-blue-50 p-6 rounded shadow">
            <p className="text-sm text-blue-600">Admin Email</p>
            <p className="text-md font-mono">{settings.VITE_ADMIN_EMAIL || 'anouarguemri1@gmail.com'}</p>
          </div>
        </div>
      )}

      {/* Season Simulation Results */}
      <h2 className="text-2xl font-bold mb-4">🏆 Season Simulation (500 Rounds)</h2>
      {loading ? (
        <p>Running Monte Carlo simulation...</p>
      ) : (
        <div className="bg-white p-6 shadow rounded">
          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={seasonSim}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="Team" angle={-45} textAnchor="end" height={100} interval={0} />
              <YAxis domain={[1, 20]} reversed={true} label={{ value: 'Average Final Rank', angle: -90, position: 'insideLeft' }} />
              <Tooltip formatter={(value) => [`Rank: ${value.toFixed(2)}`, 'Team']} />
              <Legend />
              <Bar dataKey="Avg_Final_Rank" fill="#8884d8" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}

// NOTE: Vite config doesn't actually expose environment vars like this in a build.
// In a real app, these specific settings (MODEL_TYPE, ADMIN_EMAIL) should be 
// fetched from a dedicated backend `/config` endpoint or hardcoded if non-sensitive.
// For this repo, we mimic the access for instructional clarity.
