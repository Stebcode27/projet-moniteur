import React, { useState, useEffect } from 'react';
import { Search, RefreshCw, User } from 'lucide-react';

const ExamenTable = () => {
  const [patients, setPatients] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);

  // Fonction pour charger les données depuis ton serveur Node.js
  const fetchPatients = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:5000/api/patients');
      const data = await response.json();
      setPatients(data);
    } catch (error) {
      console.error("Erreur lors de la récupération :", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPatients();
  }, []);

  // Filtrage en temps réel par nom ou ID de patient
  const filteredPatients = patients.filter(ex => 
    ex.id_patient.toLowerCase().includes(searchTerm.toLowerCase()) ||
    ex.nom.toString().includes(searchTerm)
  );

  return (
    <div style={{ padding: '20px', fontFamily: 'Segoe UI, sans-serif' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h2 style={{ color: '#2c3e50' }}>Suivi des Examens Patients</h2>
        <button 
          onClick={fetchPatients}
          style={{ padding: '8px 15px', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '5px' }}
        >
          <RefreshCw size={16} /> Actualiser
        </button>
      </div>

      {/* Barre de Recherche */}
      <div style={{ width: '50%', marginBottom: '20px', border: '2px solid black', display: 'flex', flexDirection: 'row', justifyContent: 'space-between', borderRadius: '8px' }}>
        <Search style={{ color: '#95a5a6', textAlign: 'center', padding: '10px' }} size={25} />
        <input
          className="research"
          type="search"
          placeholder="Rechercher un patient (Nom ou ID)..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          style={{
            width: '100%',
            fontSize: '16px',
            padding: '10px',
            border: '0',
            borderTopRightRadius: '8px',
            borderBottomRightRadius: '8px'
          }}
        />
      </div>

      {/* Tableau des données */}
      <div style={{ overflowX: 'auto', boxShadow: '0 4px 6px rgba(0,0,0,0.1)', borderRadius: '8px' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', backgroundColor: 'white' }}>
          <thead>
            <tr style={{ backgroundColor: '#f8f9fa', borderBottom: '2px solid #dee2e6' }}>
              <th style={cellStyle}>ID Patient</th>
              <th style={cellStyle}>Nom du Patient</th>
              <th style={cellStyle}>Salle</th>
              <th style={cellStyle}>Date / Heure</th>
              <th style={cellStyle}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr><td colSpan="5" style={{ textAlign: 'center', padding: '20px' }}>Chargement...</td></tr>
            ) : filteredPatients.length > 0 ? (
              filteredPatients.map((ex) => (
                <tr key={ex.id} style={{ borderBottom: '1px solid #eee' }}>
                  <td style={cellStyle}><strong>#{ex.id_exam}</strong></td>
                  <td style={cellStyle}><User size={14} inline /> {ex.id_patient}</td>
                  <td style={cellStyle}>{ex.salle}</td>
                  <td style={cellStyle}>{new Date(ex.date_examen).toLocaleString()}</td>
                  <td style={cellStyle}>
                    <button style={{ color: '#3498db', border: 'none', background: 'none', cursor: 'pointer' }}>
                      Voir détails
                    </button>
                  </td>
                </tr>
              ))
            ) : (
              <tr><td colSpan="5" style={{ textAlign: 'center', padding: '20px' }}>Aucun patient trouvé.</td></tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

const cellStyle = { padding: '12px 15px', textAlign: 'left' };

export default ExamenTable;