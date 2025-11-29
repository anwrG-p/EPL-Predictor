import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const AdminPanel = ({ isAdmin, token }) => {
  const [retrainStatus, setRetrainStatus] = useState('');
  const [healthStatus, setHealthStatus] = useState('Checking...');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
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
    setLoading(true);
    try {
      const response = await axios.post('/admin/retrain', null, {
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
    } finally {
      setLoading(false);
    }
  };

  const checkSystemHealth = async () => {
    try {
      const response = await axios.get('/admin/health', {
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
    return null;
  }

  return (
    <div className="max-w-4xl mx-auto animate-fade-in">
      <div className="glass-card p-8 mb-8">
        <h2 className="text-3xl font-display font-bold text-white mb-6 border-b border-white/10 pb-4 flex items-center">
          <span className="mr-3">🛠️</span> Admin Control Panel
        </h2>

        {/* System Health Status */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          <div className="bg-dark-bg/50 p-6 rounded-xl border border-white/5">
            <h3 className="text-lg font-medium text-primary-300 mb-2">System Status</h3>
            <div className="flex items-center space-x-3">
              <div className={`w-3 h-3 rounded-full ${healthStatus === 'OK' ? 'bg-green-500 shadow-[0_0_10px_rgba(34,197,94,0.5)]' : 'bg-red-500'}`}></div>
              <span className={`text-xl font-mono ${healthStatus === 'OK' ? 'text-green-400' : 'text-red-400'}`}>
                {healthStatus}
              </span>
            </div>
          </div>

          <div className="flex items-center">
            <button
              onClick={checkSystemHealth}
              className="w-full h-full btn-primary flex items-center justify-center space-x-2"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
              </svg>
              <span>Refresh Health Check</span>
            </button>
          </div>
        </div>

        {/* Model Retraining Section */}
        <div className="bg-dark-bg/50 p-6 rounded-xl border border-white/5">
          <h3 className="text-xl font-display font-bold text-white mb-4">MLOps Pipeline</h3>
          <p className="text-dark-muted mb-6">
            Trigger the automated training pipeline. This will fetch the latest EPL data, re-engineer features, tune hyperparameters, and deploy the new model artifact.
          </p>

          <button
            onClick={handleRetrainModel}
            disabled={loading}
            className={`w-full py-4 text-lg font-bold text-white rounded-xl transition-all duration-300 ${loading
                ? 'bg-gray-700 cursor-not-allowed'
                : 'bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-500 hover:to-emerald-500 shadow-lg shadow-green-900/20 hover:shadow-green-900/40 transform hover:-translate-y-0.5'
              }`}
          >
            {loading ? (
              <div className="flex items-center justify-center space-x-3">
                <svg className="animate-spin h-6 w-6 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <span>Training in Progress...</span>
              </div>
            ) : '🚀 Trigger Model Retrain'}
          </button>

          {retrainStatus && retrainStatus !== 'Failed' && !loading && (
            <div className="mt-6 p-4 bg-green-500/10 border border-green-500/20 rounded-lg text-center animate-fade-in">
              <p className="text-green-400 font-medium">{retrainStatus}</p>
            </div>
          )}

          {error && (
            <div className="mt-6 p-4 bg-red-500/10 border border-red-500/20 rounded-lg text-center animate-fade-in">
              <p className="text-red-300">Error: {error}</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default AdminPanel;
