
import React, { useState } from 'react';
import axios from 'axios';

// Shortened list for demo; in production fetch from backend
const TEAMS = ["Arsenal", "Aston Villa", "Bournemouth", "Brentford", "Brighton", "Burnley", "Chelsea", "Crystal Palace", "Everton", "Fulham", "Liverpool", "Luton", "Man City", "Man United", "Newcastle", "Nott'm Forest", "Sheffield United", "Tottenham", "West Ham", "Wolves"];

export default function Predictor({ token }) {
  const [home, setHome] = useState(TEAMS[0]);
  const [away, setAway] = useState(TEAMS[1]);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handlePredict = async () => {
    if (!token) {
      setError("Please login to make predictions.");
      return;
    }
    setError('');
    setResult(null);
    setLoading(true);
    try {
      const res = await axios.post('/predict',
        { home_team: home, away_team: away },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setResult(res.data);
    } catch (err) {
      if (err.response?.status === 429) setError("Daily limit reached! Upgrade to premium for more.");
      else setError("Prediction failed. Please try again later.");
    } finally {
      setLoading(false);
    }
  };

  const ProbabilityBar = ({ label, value, color }) => (
    <div className="mb-4">
      <div className="flex justify-between mb-1">
        <span className="text-sm font-medium text-gray-300">{label}</span>
        <span className="text-sm font-bold text-white">{(value * 100).toFixed(1)}%</span>
      </div>
      <div className="w-full bg-dark-bg rounded-full h-2.5">
        <div
          className={`h-2.5 rounded-full ${color} transition-all duration-1000 ease-out`}
          style={{ width: `${value * 100}%` }}
        ></div>
      </div>
    </div>
  );

  return (
    <div className="max-w-4xl mx-auto">
      <div className="text-center mb-12 animate-slide-up">
        <h1 className="text-5xl font-display font-bold mb-4 bg-clip-text text-transparent bg-gradient-to-r from-white to-primary-200">
          Match Predictor
        </h1>
        <p className="text-dark-muted text-lg">
          AI-powered insights for the English Premier League
        </p>
      </div>

      <div className="glass-card p-8 mb-8 animate-fade-in">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-center">

          {/* Home Team Selection */}
          <div className="space-y-2">
            <label className="block text-sm font-medium text-primary-300 uppercase tracking-wider">Home Team</label>
            <select
              className="input-field appearance-none cursor-pointer"
              value={home}
              onChange={e => setHome(e.target.value)}
            >
              {TEAMS.map(t => <option key={t} value={t} className="bg-dark-card text-white">{t}</option>)}
            </select>
          </div>

          {/* VS Badge */}
          <div className="hidden md:flex justify-center items-center">
            <div className="w-12 h-12 rounded-full bg-primary-600/20 flex items-center justify-center border border-primary-500/30">
              <span className="text-primary-400 font-bold text-sm">VS</span>
            </div>
          </div>

          {/* Away Team Selection */}
          <div className="space-y-2">
            <label className="block text-sm font-medium text-red-400 uppercase tracking-wider">Away Team</label>
            <select
              className="input-field appearance-none cursor-pointer"
              value={away}
              onChange={e => setAway(e.target.value)}
            >
              {TEAMS.map(t => <option key={t} value={t} className="bg-dark-card text-white">{t}</option>)}
            </select>
          </div>
        </div>

        <div className="mt-8 flex justify-center">
          <button
            onClick={handlePredict}
            disabled={loading}
            className={`btn-primary w-full md:w-auto min-w-[200px] flex justify-center items-center ${loading ? 'opacity-75 cursor-not-allowed' : ''}`}
          >
            {loading ? (
              <svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
            ) : 'Predict Outcome'}
          </button>
        </div>

        {error && (
          <div className="mt-6 p-4 bg-red-500/10 border border-red-500/20 text-red-200 rounded-lg text-center animate-fade-in">
            {error}
          </div>
        )}
      </div>

      {result && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 animate-slide-up">
          {/* Probabilities Card */}
          <div className="glass-card p-6">
            <h2 className="text-2xl font-display font-bold mb-6 text-white border-b border-white/10 pb-2">Match Probabilities</h2>
            <div className="space-y-6">
              <ProbabilityBar label={`${home} Win`} value={result.probs.Home} color="bg-primary-500" />
              <ProbabilityBar label="Draw" value={result.probs.Draw} color="bg-gray-400" />
              <ProbabilityBar label={`${away} Win`} value={result.probs.Away} color="bg-red-500" />
            </div>
          </div>

          {/* Explainability Card */}
          <div className="glass-card p-6">
            <h2 className="text-2xl font-display font-bold mb-6 text-white border-b border-white/10 pb-2">AI Analysis</h2>
            <div className="bg-white/5 rounded-lg p-2 border border-white/10">
              <img src={`http://localhost:8000${result.shap_url}`} alt="SHAP Plot" className="w-full rounded opacity-90 hover:opacity-100 transition-opacity" />
            </div>
            <p className="mt-4 text-sm text-dark-muted text-center">
              Feature importance showing key factors influencing the prediction.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
