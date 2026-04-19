import './Footer.css';
import { NavLink } from 'react-router-dom';

export default function Footer(){

    return(
        <footer>
            <div className="footer-container">
                <span className="copy">&copy; lifekeeper 2026</span><br />
                <span>Projet Académique DUT GBM. Consultez notre page de <NavLink to='/about'>renseignements</NavLink></span>
                <center>
                    <div className="logo-container">
                    <img src="../../assets/logo_iut.png" alt="" />
                    </div>
                </center>
            </div>
        </footer>
    );
}