import React from 'react';
import './styles/Home.css';
import CardHome from '../components/CardHome';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { FaAddressBook, FaBezierCurve, FaDigitalTachograph, FaGraduationCap } from 'react-icons/fa';
import { LuActivity } from "react-icons/lu";

const Home = () => {

  const {user, logout} = useAuth();
  const navigate = useNavigate();

  return (
    <div className="home-wrapper">
      <div className='entete'>
        {/* 1. Section Texte / Titre */}
        <div className="left-section">
          <div className="hero-text">
            <h1>Assurez une meilleure santé !</h1>
          </div>
          {/* 2. La Barre de Recherche (Style Doctolib) */}
          <div className="search-container">
            <div className="search-input-group">
              <input 
                type="text" 
                placeholder="Nom du patient, ID patient, examen" 
              />
            </div>
            <button className="search-btn">Rechercher</button>
          </div>      
        </div>
        {/* 3. Section Image avec la forme bleue (Blob) */}
        <div className="hero-image-section">
          {/* La forme arrondie bleue qui bouge derrière */}
          <div className="blue-shape"></div>
          
          {/* Ton image d'illustration d'examen médical */}
          <img 
            src='../../assets/muhammad-noor-ridho-jnejsp8IB-w-unsplash.png' 
            className="doctor-illustration" 
            alt="Examen médical échographie" 
          />
        </div>
      </div>

      <div className="salutation">
        <h2>Bonjour, <strong>{user ? user.name : "User"}</strong></h2>
      </div>

      <div className="section-option">
        <div className="option">
          <center>
            <div className="option-top">
              <FaAddressBook style={{color: '#7ab4f6'}} className='icon-section' />
            </div>
            <div className="option-contenu">
              Consultez la liste des examens et des patients présents dans la base de données.
            </div>
            <div className="option-bottom">
              <button onClick={() => {navigate("/examen")}}>Voir les derniers examens</button>
            </div>
          </center>
        </div>
        <div className="option">
          <center>
            <div className="option-top">
              <LuActivity style={{color: 'lime'}} className='icon-section' />
            </div>
            <div className="option-contenu">
              Effectuez une analyse statistique sur les resultats des examens patients.
            </div>
            <div className="option-bottom">
              <button onClick={() => {navigate("/stats")}}>Lancer l'analyse</button>
            </div>
          </center>
        </div>
      </div>

      

    </div>
  );
};

export default Home;