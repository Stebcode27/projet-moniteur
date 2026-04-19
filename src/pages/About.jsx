import React from "react";
import './styles/About.css';

const About = () => {
    return (
        <div className="about">
            <div className="top-about">
                <h1>About Us</h1>
                <p>Life Keeper, la solution de gestion des examens médicaux</p>
            </div>
            <h2>Ce qui nous motive!</h2>
            <div className="explications">
                <div className="element">
                    <div className="top-element">
                        <span>Notre Objectif</span>
                        <p>Nous visons à fournir une solution complète pour la gestion des examens médicaux, en améliorant l'efficacité et la qualité des soins prodigués aux patients.</p>
                    </div>
                    <div className="img-container">
                        <img src="../../assets/croisebras.jpg" alt="" />
                    </div>
                </div>
                <div className="element">
                    <div className="img-container">
                        <img src="../../assets/salle.jpg" alt="" />
                    </div>
                    <div className="top-element">
                        <span>Notre Mission</span>
                        <p>Nous nous engageons à simplifier la gestion des examens médicaux pour les professionnels de santé, afin de leur permettre de se concentrer sur ce qui compte le plus : le bien-être de leurs patients.</p>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default About;