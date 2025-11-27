import React, { useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Login from './components/Login';
import Predictor from './components/Predictor';
import AdminPanel from './components/AdminPanel';
import Layout from './components/Layout';

const ProtectedRoute = ({ children }) => {
  const token = localStorage.getItem('token');
  return token ? children : <Navigate to="/login" />;
};

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/" element={<ProtectedRoute><Layout><Predictor /></Layout></ProtectedRoute>} />
        <Route path="/admin" element={<ProtectedRoute><Layout><AdminPanel /></Layout></ProtectedRoute>} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
