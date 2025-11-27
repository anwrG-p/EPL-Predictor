
import React, { useState } from 'react';
import axios from 'axios';

// Shortened list for demo; in production fetch from backend
const TEAMS = ["Arsenal", "Aston Villa", "Bournemouth", "Brentford", "Brighton", "Burnley", "Chelsea", "Crystal Palace", "Everton", "Fulham", "Liverpool", "Luton", "Man City", "Man United", "Newcastle", "Nott'm Forest", "Sheffield United", "Tottenham", "West Ham", "Wolves"];

export default function Predictor() {
  const [home, setHome] = useState(TEAMS[0]);
  const [away, setAway] = useState(TEAMS[1]);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  const handlePredict = async () => {
    setError('');
    setResult(null);
    try {
      const token = localStorage.getItem('token');
      const res = await axios.post('http://localhost:8000/predict', 
        { home_team: home, away_team: away },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setResult(res.data);
    } catch (err) {
      if(err.response?.status === 429) setError("Daily limit reached!");
      else setError("Prediction failed. Check team names or server.");
    }
  };

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <h1 className="text-3xl font-bold mb-6 text-gray-800">Match Predictor</h1>
      
      <div className="flex gap-4 mb-6">
        <select className="p-2 border rounded w-1/2" value={home} onChange={e => setHome(e.target.value)}>
          {TEAMS.map(t => <option key={t} value={t}>{t} (Home)</option>)}
        </select>
        <select className="p-2 border rounded w-1/2" value={away} onChange={e => setAway(e.target.value)}>
          {TEAMS.map(t => <option key={t} value={t}>{t} (Away)</option>)}
        </select>
      </div>

      <button onClick={handlePredict} className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700 transition">
        Predict Outcome
      </button>

      {error && <div className="mt-4 p-4 bg-red-100 text-red-700 rounded">{error}</div>}

      {result && (
        <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-8">
          <div className="bg-white p-6 shadow rounded">
            <h2 className="text-xl font-bold mb-4">Probabilities</h2>
            <div className="space-y-2">
              <div className="flex justify-between"><span>Home Win:</span> <span className="font-mono">{(result.probs.Home * 100).toFixed(1)}%</span></div>
              <div className="flex justify-between"><span>Draw:</span> <span className="font-mono">{(result.probs.Draw * 100).toFixed(1)}%</span></div>
              <div className="flex justify-between"><span>Away Win:</span> <span className="font-mono">{(result.probs.Away * 100).toFixed(1)}%</span></div>
            </div>
          </div>
          <div className="bg-white p-6 shadow rounded">
            <h2 className="text-xl font-bold mb-4">Explainability (SHAP)</h2>
            <img src={`http://localhost:8000${result.shap_url}`} alt="SHAP Plot" className="w-full" />
          </div>
        </div>
      )}
    </div>
  );
}
