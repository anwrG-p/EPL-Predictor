import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

// NOTE on API_URL: In a production environment (like GitHub Pages),
// you MUST replace 'http://localhost:8000' with your live backend URL (e.g., https://your-fastapi-app.com).
// For local Docker use, 'http://localhost:8000' is correct.
const API_URL = 'http://localhost:8000';

const AdminPanel = ({ isAdmin, token }) => {
  const [retrainStatus, setRetrainStatus] = useState('');
  const [healthStatus, setHealthStatus] = useState('Checking...');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  // Redirect if not logged in or not admin
  useEffect(() => {
    if (!token || !isAdmin) {
      navigate('/login');
    }
  }, [isAdmin, token, navigate]);

  const handleRetrainModel = async () => {
    setRetrainStatus('Training...');
    setError('');
    try {
      const response = await axios.post(`${API_URL}/admin/retrain`, null, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
        timeout: 600000, // 10 minutes timeout for long training process
      });
      setRetrainStatus(`Training Complete! ${response.data.message}`);
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || 'Retraining failed. Check backend logs.');
      setRetrainStatus('Failed');
    }
  };

  const checkSystemHealth = async () => {
    try {
      const response = await axios.get(`${API_URL}/admin/health`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      setHealthStatus(response.data.status);
    } catch (err) {
      console.error(err);
      setHealthStatus('System Down or Unauthorized');
    }
  };

  useEffect(() => {
    if (isAdmin && token) {
      checkSystemHealth();
    }
  }, [isAdmin, token]);

  if (!isAdmin) {
    return null; // Should redirect, but just in case
  }

  return (
    <div className="p-8 max-w-2xl mx-auto bg-gray-900 rounded-xl shadow-2xl">
      <h2 className="text-3xl font-extrabold text-white mb-6 border-b border-indigo-600 pb-2">
        🛠️ Admin Control Panel
      </h2>

      {/* System Health Status */}
      <div className="mb-8 p-4 bg-gray-800 rounded-lg">
        <h3 className="text-xl font-semibold text-indigo-400 mb-2">System Health</h3>
        <p className={`text-lg font-mono ${healthStatus === 'OK' ? 'text-green-400' : 'text-yellow-400'}`}>
          Status: {healthStatus}
        </p>
        <button
          onClick={checkSystemHealth}
          className="mt-3 px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 transition"
        >
          Refresh Health Check
        </button>
      </div>

      {/* Model Retraining Section */}
      <div className="p-4 bg-gray-800 rounded-lg">
        <h3 className="text-xl font-semibold text-indigo-400 mb-4">Model Retraining (MLOps)</h3>
        <p className="text-gray-400 mb-4">
          Fetch the latest EPL data, re-engineer features (Elo/Form), re-tune, and save the updated model artifact. This may take several minutes.
        </p>
        
        <button
          onClick={handleRetrainModel}
          disabled={retrainStatus === 'Training...'}
          className={`w-full px-6 py-3 text-lg font-bold text-white rounded-lg transition ${
            retrainStatus === 'Training...'
              ? 'bg-yellow-600 cursor-not-allowed'
              : 'bg-green-600 hover:bg-green-700'
          }`}
        >
          {retrainStatus === 'Training...' ? 'Processing...' : 'Trigger Model Retrain'}
        </button>

        {retrainStatus && retrainStatus !== 'Failed' && (
          <p className="mt-4 text-center text-green-400 font-medium">
            {retrainStatus}
          </p>
        )}

        {error && (
          <div className="mt-4 p-3 bg-red-800/50 border border-red-500 rounded text-red-300">
            Error: {error}
          </div>
        )}
      </div>
    </div>
  );
};

export default AdminPanel;
