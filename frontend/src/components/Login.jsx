import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);
    try {
      const res = await axios.post('http://localhost:8000/token', formData);
      localStorage.setItem('token', res.data.access_token);
      navigate('/');
    } catch (err) {
      alert("Login failed");
    }
  };

  return (
    <div className="h-screen flex items-center justify-center bg-gray-100">
      <form onSubmit={handleLogin} className="bg-white p-8 rounded shadow-md w-96">
        <h2 className="text-2xl mb-4 font-bold">EPL Login</h2>
        <input className="w-full mb-3 p-2 border" type="email" placeholder="Email" value={email} onChange={e=>setEmail(e.target.value)} />
        <input className="w-full mb-4 p-2 border" type="password" placeholder="Password" value={password} onChange={e=>setPassword(e.target.value)} />
        <button className="w-full bg-green-600 text-white p-2 rounded">Sign In</button>
      </form>
    </div>
  );
}
