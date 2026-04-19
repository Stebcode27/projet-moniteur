import React, { useEffect, useState } from 'react';
import { NavLink } from 'react-router-dom';
import { FaHome, FaInfoCircle, FaBars, FaTimes, FaAddressBook } from 'react-icons/fa';
import {LuSquareActivity} from 'react-icons/lu';
import './Navbar.css';

const Navbar = () => {
  const [isOpen, setIsOpen] = useState(true);
  const [salle, setSalle] = useState({});

  const fetchSalleMoniteur = async () => {

    try {
      const response = await fetch('http://localhost:5000/api/salle');
      const data = await response.json();
      setSalle(data);
    } catch (error) {
      console.log(error);
    }
  }

  useEffect(() => {fetchSalleMoniteur()}, []);

  const toggleNavbar = () => setIsOpen(!isOpen);

  return (
      <nav className={`navbar ${isOpen ? "open" : "closed"}`}>
        <div className="navigation">
          <button className="toggle-btn" onClick={toggleNavbar}>
            {isOpen ? <FaTimes className='nav-icon'/> : <FaBars className='nav-icon'/>}
          </button>
          <ul className="nav-links">
            <li>
              <NavLink to="/" end className={({ isActive }) => isActive ? "active" : ""}>
                <FaHome className="nav-icon" />
                {isOpen && <span>Accueil</span>}
              </NavLink>
            </li>
            <li>
              <NavLink to="/examen" className={({ isActive }) => isActive ? "active" : ""}>
                <FaAddressBook className='nav-icon' />
                {isOpen && <span>Examens</span>}
              </NavLink>
            </li>
            <li>
              <NavLink to="/stats" className={({ isActive }) => isActive ? "active" : ""}>
                <LuSquareActivity className="nav-icon" />
                {isOpen && <span>Statistiques</span>}
              </NavLink>
            </li>
            <li>
              <NavLink to="/about" className={({ isActive }) => isActive ? "active" : ""}>
                <FaInfoCircle className="nav-icon" />
                {isOpen && <span>À Propos</span>}
              </NavLink>
            </li>
          </ul>
        </div>

        {isOpen && 
          <div className="salle">
            <span>Le moniteur est dans la <strong>{salle.salle}</strong></span>
          </div>
        }
      </nav>
  );
};

export default Navbar;