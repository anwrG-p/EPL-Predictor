import React from 'react';
import { HashRouter as Router, Routes, Route, NavLink, Navigate } from 'react-router-dom';
import axios from 'axios';
import Predictor from './components/Predictor.jsx';
import SeasonView from './components/SeasonView.jsx';
import ModelsView from './components/ModelsView.jsx';
import './index.css';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
axios.defaults.baseURL = API_URL;

function App() {
  const getNavClass = ({ isActive }) =>
    `px-4 py-2 rounded-full text-sm font-medium transition-all duration-200 min-h-[40px] inline-flex items-center ${
      isActive
        ? 'bg-[#C6F432] text-[#0E1512] font-semibold shadow-sm'
        : 'text-[#9DB0A5] hover:text-[#E8EFE9] hover:bg-[#16201B]'
    }`;

  return (
    <Router>
      <div className="min-h-screen bg-[#0E1512] text-[#E8EFE9] flex flex-col justify-between selection:bg-[#C6F432]/30 selection:text-[#0E1512]">
        <div className="max-w-[1280px] w-full mx-auto px-4 sm:px-8 py-6 box-border">
          {/* Header */}
          <header className="flex justify-between items-center flex-wrap gap-4 mb-8">
            {/* Logo */}
            <NavLink to="/" className="flex items-center gap-3 text-xl font-heading font-bold text-[#E8EFE9] hover:opacity-90 transition-opacity">
              <svg width="32" height="32" viewBox="0 0 32 32" aria-hidden="true" className="shrink-0">
                <circle cx="16" cy="16" r="14" fill="none" stroke="#C6F432" strokeWidth="2.5"></circle>
                <path d="M16 8l6 4v7l-6 4-6-4v-7z" fill="#C6F432"></path>
              </svg>
              <span>EPL Predictor</span>
            </NavLink>

            {/* Pill Navigation */}
            <nav className="flex items-center gap-1 sm:gap-2 p-1 bg-[#16201B] border border-[#26352D] rounded-full" aria-label="Main">
              <NavLink to="/" className={getNavClass} end>
                Match
              </NavLink>
              <NavLink to="/season" className={getNavClass}>
                Season
              </NavLink>
              <NavLink to="/models" className={getNavClass}>
                Models
              </NavLink>
            </nav>
          </header>

          {/* Main Views */}
          <main>
            <Routes>
              <Route path="/" element={<Predictor />} />
              <Route path="/season" element={<SeasonView />} />
              <Route path="/models" element={<ModelsView />} />
              <Route path="/admin" element={<Navigate to="/models" replace />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </main>
        </div>

        {/* Footer */}
        <footer className="border-t border-[#26352D] py-6 mt-12 bg-[#0E1512]">
          <div className="max-w-[1280px] mx-auto px-4 sm:px-8 flex flex-col sm:flex-row justify-between items-center gap-4 text-xs text-[#9DB0A5]">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-[#C6F432]"></span>
              <span>Premier League Analytics & Machine Learning Intelligence</span>
            </div>
            <div className="flex gap-6">
              <a
                href="https://github.com/anwrG-p/EPL-Predictor"
                target="_blank"
                rel="noreferrer"
                className="hover:text-[#E8EFE9] transition-colors"
              >
                GitHub Repository
              </a>
              <span>MIT License</span>
            </div>
          </div>
        </footer>
      </div>
    </Router>
  );
}

export default App;
