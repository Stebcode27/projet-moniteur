import React, { useEffect, useState } from 'react';
import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import './styles/Login.css';
import Loader from '../components/Loader';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = (e) => {
    e.preventDefault();

    setLoading(true);
    fetchUser();
    if (email && password) {
      users.forEach(user => {
        if(user.email===email && user.password===password){
          const userData = { 
            name: email.split('@')[0], // On prend le début de l'email comme nom
            email: email 
          };

          login(userData); // On met à jour le contexte global
          navigate('/');   // On redirige vers l'accueil
        }
      });
    } else {
      alert("Veuillez remplir tous les champs");
    }
  };

  const fetchUser = async () => {
    try{
      const response = await fetch('http://localhost:5000/api/login');
      const data = await response.json();
      setUsers(data);
      setLoading(false);
    }
    catch (err){
      console.error("Erreur lors de la récupération: ", err)
    }
  }

  useEffect(() => {
    fetchUser();
  }, []);

  return (
    <div className="login-container">
      {loading ? (<Loader/>) : (
        <form className="login-form" onSubmit={handleSubmit}>
          <h1>Connexion</h1>
          <div className="input-group">
            <label>Email</label>
            <input 
              type="email" 
              value={email} 
              onChange={(e) => setEmail(e.target.value)}
              placeholder="votre@email.com"
              required
            />
          </div>
          <div className="input-group">
            <label>Mot de passe</label>
            <input 
              type="password" 
              value={password} 
              onChange={(e) => setPassword(e.target.value)} 
              placeholder="••••••••"
              required
            />
          </div>
          <button type="submit" className="login-btn">Se connecter</button>
          <div className="inscription">
            <NavLink to='/sign' className="link-inscription" >
              S'incrire
            </NavLink>
          </div>
        </form>
      )}
    </div>
  );
};

export default Login;