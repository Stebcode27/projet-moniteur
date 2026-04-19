import React from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import './Topbar.css';

const Topbar = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  return (
    <header className="topbar">
      <div className="topbar-left">
        <img src="../../assets/logo_iut.png" alt="" className="logo" onClick={() => navigate("/")}/>
        <h2>Life Keeper</h2>
      </div>

      <div className="topbar-right">
        {user ? (
          <div className="user-info">
            <span><strong>{user.name}</strong></span>
            <button className="logout-btn" onClick={logout}>Déconnexion</button>
          </div>
        ) : (
          <button className="login-btn">Connexion</button>
        )}
      </div>
    </header>
  );
};

export default Topbar;