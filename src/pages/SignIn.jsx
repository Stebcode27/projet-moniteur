import React, { useState } from "react";
import { NavLink, useNavigate } from "react-router-dom";
import './styles/SignIn.css';

const SignIn = () => {

    const navigate = useNavigate();

    const [formData, setFormData] = useState({
        id:'',
        fullName:'',
        email:'',
        phone:'',
        password:'',
        id_service:''
    });

    const handleChange = (e) => {
        setFormData({...formData, [e.target.name]: e.target.value});
    };

    const handleSubmit = async (e) => {
        e.preventDefault();

        try {
            const response = await fetch("http://localhost:5000/api/doctors/signup",{
                method: 'POST',
                headers: {'Content-Type':'application/json'},
                body: JSON.stringify(formData),
            });

            if(response.ok){
                alert("Médecin enregistré avec succès !");
                navigate('/login');
            }else{
                alert("Erreur lors de l'inscription.");
            }
        } catch (error) {
            console.error("Erreur réseau: ", error);
        }
    };

    return(
        <div className="container">
            <div className="sign-container">
                <form onSubmit={handleSubmit} className="inscription-form">
                    <center><h1>Inscription</h1></center>
                    <input type="text"
                        name="id"
                        value={formData.id}
                        placeholder="ID Médecin"
                        onChange={handleChange}
                        required
                    />
                    <input type="text"
                        name="fullName"
                        value={formData.fullName}
                        placeholder="Nom Complet"
                        onChange={handleChange}
                        required
                    />
                    <input type="email"
                        name="email"
                        value={formData.email}
                        placeholder="johndoe@yahoo.fr"
                        onChange={handleChange}
                        required
                    />
                    <input type="tel"
                        name="phone"
                        value={formData.phone}
                        max={9}
                        placeholder="6XXXXXXXX"
                        onChange={handleChange}
                        required
                    />
                    <input type="password"
                        name="password"
                        value={formData.password}
                        placeholder="Mot de Passe"
                        required
                        onChange={handleChange}
                    />
                    <select name="id_service" value={formData.id_service} onChange={handleChange} required>
                        <option value="">Sélectionner un service</option>
                        <option value="Urgences">Urgences</option>
                        <option value="Bloc Opératoire">Bloc Opératoire</option>
                        <option value="Réanimation">Réanimation</option>
                        <option value="Néonatalogie">Néonatalogie</option>
                    </select>
                    <center>
                        <button type="submit" className="sign-button">S'inscrire</button>
                    </center>
                    <div className="connexion">
                        <NavLink to='/login' className="link-connexion" >
                            Se connecter
                        </NavLink>
                    </div>
                </form>
            </div>
        </div>
    );
}

export default SignIn;