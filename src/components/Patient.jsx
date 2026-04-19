import { User } from 'lucide-react';
import './Patient.css';

const Patient = ({ dataPatient }) => {

    const calculateIMC = (p, t) => {
        let poids = parseFloat(p);
        let taille = parseFloat(t);

        return parseInt(poids / Math.pow(taille, 2));
    }

    return (
        <div className="patient">
            <div className="patient-top">
                <center><User size={50} inline/></center>
                <div className="patient-id">{dataPatient.id}</div>
            </div>
            <div className="patient-container">
                <ul>
                    <li>
                        <span className="champ">Nom: </span>
                        <span className="value">{dataPatient.nom}</span>
                    </li>
                    <li>
                        <span className="champ">Age: </span>
                        <span className="value">{dataPatient.age} ans</span>
                    </li>
                    <li>
                        <span className="champ">Sexe: </span>
                        <span className="value">{dataPatient.sexe==='M' ? "Masculin" : "Féminin"}</span>
                    </li>
                    <li>
                        <span className="champ">Poids: </span>
                        <span className="value">{dataPatient.poids} (kg)</span>
                    </li>
                    <li>
                        <span className="champ">Taille: </span>
                        <span className="value">{dataPatient.taille} (m)</span>
                    </li>
                    <li>
                        <span className="champ">IMC: </span>
                        <span className="value">{calculateIMC(dataPatient.poids, dataPatient.taille)}</span>
                    </li>
                </ul>
                <button type="button">Modifier les informations</button>
            </div>
        </div>
    );
}

export default Patient;