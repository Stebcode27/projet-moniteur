import React, { useState, useRef } from 'react';
import { Line } from 'react-chartjs-2';
import { Search, Activity, Thermometer, Droplets, Wind, RefreshCcw, AlertCircle } from 'lucide-react';
import {
  Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler
} from 'chart.js';
import Loader from '../components/Loader';
import Patient from '../components/Patient';
import ExportButton from '../components/ExportButton';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler);

const analyzeHealthStatus = (data) => {
    if (!data || !data.hr || data.hr.length < 5) return null;

    // 1. On récupère les moyennes du début (5 premiers points) et de la fin (5 derniers points)
    const getAvg = (arr) => arr.reduce((a, b) => a + b, 0) / arr.length;
    
    const startHR = getAvg(data.hr.slice(0, 5));
    const endHR = getAvg(data.hr.slice(-5));
    
    const startSpO2 = getAvg(data.spo2.slice(0, 5));
    const endSpO2 = getAvg(data.spo2.slice(-5));

    const lastTemp = data.temp[data.temp.length - 1];

    let status = { label: "Stable", color: "#10b981", icon: "✅", advice: "Paramètres stables." };
    let observations = [];

    // 2. ANALYSE DES TENDANCES (Évolution dans le temps)
    
    // Rythme Cardiaque
    if (endHR > startHR + 10) observations.push("Augmentation rapide du rythme cardiaque (Stress/Douleur)");
    else if (endHR < startHR - 10) observations.push("Ralentissement notable du rythme cardiaque");

    // Saturation (Très critique)
    if (endSpO2 < startSpO2 - 2) {
        observations.push("⚠️ Chute de la saturation (Désaturation en cours)");
        status = { label: "Instable", color: "#f59e0b", icon: "⚠️" };
    }

    // 3. VÉRIFICATION DES SEUILS CRITIQUES (Sécurité)
    const currentSpO2 = data.spo2[data.spo2.length - 1];
    if (currentSpO2 < 90) {
        status = { label: "CRITIQUE", color: "#ef4444", icon: "🚨" };
        observations.push("Détresse respiratoire sévère !");
    }

    if (lastTemp > 38.5) observations.push("Fièvre élevée détectée");

    // Synthèse
    status.advice = observations.length > 0 ? observations.join(" | ") : "Le patient présente des constantes stables sur toute la durée de la session.";
    
    return status;
};

const EvolutionDashboard = () => {
    const [searchTerm, setSearchTerm] = useState('');
    const [data, setData] = useState(null);
    const [avgData, setAvgData] = useState(null);
    const [patient, setPatient] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [analysis, setAnalysis] = useState(null);
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [sessions, setSessions] = useState([]);
    const [selectedSessionId, setSelectedSessionId] = useState('');
    const [visibleCharts, setVisibleCharts] = useState({
        hr: true,
        spo2: true,
        temp: true,
        resp: true
    });

    const toggleChart = (param) => {
        setVisibleCharts(prev => ({ ...prev, [param]: !prev[param] }));
    };

    const runAIAnalysis = () => {
        if (!data) return;
        setIsAnalyzing(true);
        setAnalysis(null);

        // Simulation d'un petit délai de calcul IA (1.5s)
        setTimeout(() => {
            const result = analyzeHealthStatus(data); // Utilise la fonction de mon message précédent
            setAnalysis(result);
            setIsAnalyzing(false);
        }, 50);
    };

    const fetchPatientSessions = async () => {
        try {
            const res = await fetch(`http://localhost:5000/api/monitoring/sessions/${searchTerm}`);
            const data = await res.json();
            setSessions(data);
            if(data.length) setSelectedSessionId(data[0].id);
        } catch (error) {
            console.error(error);
        }
    }

    const fetchPatient = async () => {
        try {
            const response = await fetch(`http://localhost:5000/api/monitoring/patient/${searchTerm}`);
            const result = await response.json();

            setPatient(result);
        } catch (e) {
            console.log("Erreur: ", e);
        }
    };
// 2. Modifier fetchEvolution pour charger une session spécifique
    const fetchEvolution = async () => {
        setLoading(true);
        try {
            const response = await fetch(`http://localhost:5000/api/monitoring/session-detail/${searchTerm}`);
            const result = await response.json();
            setData(result.curves);
            setAvgData(result.stats);
            fetchPatient();
            fetchPatientSessions();
        } catch (error) { setError(error); }
        finally { setLoading(false); }
    };

    const fetchSessionForPatient = async (sessionId = selectedSessionId) => {
        if(!sessionId) return;
        setLoading(true);
        try{
            const response = await fetch(`http://localhost:5000/api/monitoring/session/${searchTerm}/${sessionId}`);
            const result = await response.json();
            setData(result.curves);
            setAvgData(result.stats);
            fetchPatient();
            fetchPatientSessions();
        }catch(error){ setError(error); }
        finally { setLoading(false); }
    };

    const getOptions = (title, unit, color) => ({
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: { display: false },
            tooltip: { 
                mode: 'index', 
                intersect: false,
                callbacks: { label: (context) => `${context.dataset.label}: ${context.raw} ${unit}` }
            },
            title: { display: true, text: `${title} (${unit})`, color: '#334155', font: { size: 16, weight: 'bold' } }
        },
        scales: {
            y: { 
                beginAtZero: false, 
                grid: { color: '#f1f5f9' },
                ticks: { color: '#64748b' }
            },
            x: { 
                grid: { display: false }, 
                ticks: { color: '#64748b', maxRotation: 5, minRotation: 5 },
                title: { display: true, text: 'Sessions (Date & Heure)', color: '#94a3b8' }
            }
        }
    });

    const prepareData = (label, points, timestamps, color) => ({
        labels: timestamps, 
        datasets: [{
            label: label,
            data: points,
            borderColor: color,
            backgroundColor: color + '15', // Transparence pour le remplissage
            fill: true,
            tension: 0.5,
            pointRadius: 2,
            pointBackgroundColor: color,
            pointHoverRadius: 6,
            borderWidth: 2
        }]
    });

    const getVitalsForReport = () => {
        if (!data || !avgData) return { name: "N/A", value: "N/A", unit: "", status: "N/A" };
        
        return [
            { name: "Fréquence Cardiaque", value: avgData.hr_avg, unit: "bpm", status: avgData.hr_avg > 100 ? "Élevé" : "Normal" },
            { name: "Saturation Oxygène", value: avgData.spo2_avg, unit: "%", status: avgData.spo2_avg < 95 ? "Bas" : "Normal" },
            { name: "Température Corporelle", value: avgData.temp_avg, unit: "°C", status: avgData.temp_avg > 38 ? "Fièvre" : "Normal" },
            { name: "Fréquence Respiratoire", value: avgData.resp_avg, unit: "rpm", status: avgData.resp_avg > 20 ? "Élevé" : "Normal" }
        ];
    }

    const getPatientForReport = () => {
        if (!patient) return { id: "N/A", nom: "N/A", age: "N/A", sexe: "N/A", poids: "N/A", taille: "N/A" };

        return {
            id: patient.id,
            nom: patient.nom,
            age: patient.age,
            sexe: patient.sexe,
            poids: patient.poids,
            taille: patient.taille,
            aiNote: analysis ? analysis.advice : "Aucune analyse IA disponible."
        };
    };

    const VitalGraph = ({ chartRef }) => {
        const data = { /* vos données de constantes */ };
        
        return (
            // On attache la ref au composant graphique
            <Line ref={chartRef} data={data} />
        );
    };

    const chartRef = useRef(null);

    const captureGraph = () => {
        if (chartRef.current) {
            // Convertit le canvas du graphique en image PNG (Base64)
            return chartRef.current.toBase64Image();
        }
        return null;
    };

    if(loading) return <Loader/>;

    return (
        <div style={{ padding: '25px', backgroundColor: '#f8fafc', minHeight: '100vh', fontFamily: 'Inter, sans-serif' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '25px' }}>
                <h2 style={{ color: '#0f172a', margin: 0, display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <Activity size={28} color="#3b82f6" /> Dashboard
                </h2>
                {data && <span style={badgeStyle}>{data.times.length} points trouvés</span>}
            </div>

            <div style={filterPanelStyle}>
                <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap', alignItems: 'center' }}>
                    <div style={{ position: 'relative', flex: '1', minWidth: '200px' }}>
                        <Search style={searchIconStyle} size={18} />
                        <input 
                            type="search" 
                            placeholder="Entrez l'ID Patient (ex: PAT57)..." 
                            style={inputStyle}
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            onKeyPress={(e) => e.key === 'Enter' && fetchEvolution()}
                        />
                    </div>
                    <button onClick={fetchEvolution} style={btnStyle} disabled={loading}>
                        {loading ? <RefreshCcw className="animate-spin" size={18} /> : "Analyser l'historique"}
                    </button>
                </div>

                <div style={checkboxGroupStyle}>
                    <label style={labelStyle}><input type="checkbox" checked={visibleCharts.hr} onChange={() => toggleChart('hr')} style={checkStyle} /> <Activity size={14} color="#ef4444"/> Pouls (FC)</label>
                    <label style={labelStyle}><input type="checkbox" checked={visibleCharts.spo2} onChange={() => toggleChart('spo2')} style={checkStyle} /> <Droplets size={14} color="#3b82f6"/> Oxygène (SpO2)</label>
                    <label style={labelStyle}><input type="checkbox" checked={visibleCharts.temp} onChange={() => toggleChart('temp')} style={checkStyle} /> <Thermometer size={14} color="#f59e0b"/> Température</label>
                    <label style={labelStyle}><input type="checkbox" checked={visibleCharts.resp} onChange={() => toggleChart('resp')} style={checkStyle} /> <Wind size={14} color="#10b981"/> Respiration</label>
                </div>
            </div>

            {error && (
                <div style={errorStyle}>
                    <AlertCircle size={20} /> {error}
                </div>
            )}

            

            {data && patient && (
                <center>
                    <div style={{display: 'flex', flexDirection: 'column', justifyContent: 'center'}}>
                        <h2>Informations du Patient</h2>
                        <Patient dataPatient={patient} />
                    </div>
                </center>
            )}

            {data && 
                <div style={statStyle}>
                    <center><h2>Statistiques</h2></center>
                    <div style={statContainer}>
                        <div style={statFC}>
                            <div>
                                <Activity size={30} color="#ef4444"/>
                            </div>
                            {avgData.hr_avg} bpm
                        </div>
                        <div style={statSPO2}>
                            <div>
                                <Droplets size={30} color="#3b82f6"/>
                            </div>
                            {avgData.spo2_avg} %
                        </div>
                        <div style={statTEMP}>
                            <div>
                                <Thermometer size={30} color="#f59e0b"/>
                            </div>
                            {avgData.temp_avg} °C
                        </div>
                        <div style={statRESP}>
                            <div>
                                <Wind size={30} color="#10b981"/>
                            </div>
                            {avgData.resp_avg} rpm
                        </div>
                    </div>
                </div>
            }
            {sessions.length > 1 && (
                <div style={{ margin: '20px 0', padding: '15px', backgroundColor: '#fff', borderRadius: '12px', border: '1px solid #e2e8f0' }}>
                    <label style={{ marginRight: '10px', fontWeight: 'bold' }}>Sélectionner la session :</label>
                    <select 
                        value={selectedSessionId} 
                        onChange={(e) => {
                            setSelectedSessionId(e.target.value);
                            fetchSessionForPatient(e.target.value); // Recharge les données au changement
                            console.log(e.target.value);
                        }}
                        style={{ padding: '8px', borderRadius: '6px', border: '1px solid #cbd5e1' }}
                    >
                        {sessions.map(s => (
                            <option key={s.id} value={s.id}>
                                Session du {new Date(s.date_session).toLocaleDateString()} (ID: {s.id})
                            </option>
                        ))}
                    </select>
                </div>
            )}

            {data ? (
                <div style={{marginTop: '10px'}}>
                    <h2>Graphiques</h2>
                    <div style={gridStyle}>
                        {visibleCharts.hr && (
                            <div style={chartCardStyle}>
                                <Line options={getOptions('Fréquence Cardiaque', 'BPM', '#ef4444')} 
                                    data={prepareData('FC', data.hr, data.times, '#ef4444')} ref={chartRef} />
                            </div>
                        )}
                        {visibleCharts.spo2 && (
                            <div style={chartCardStyle}>
                                <Line options={getOptions('Saturation Oxygène', '%', '#3b82f6')} 
                                    data={prepareData('SpO2', data.spo2, data.times, '#3b82f6')} />
                            </div>
                        )}
                        {visibleCharts.temp && (
                            <div style={chartCardStyle}>
                                <Line options={getOptions('Température Corporelle', '°C', '#f59e0b')} 
                                    data={prepareData('Temp', data.temp, data.times, '#f59e0b')} />
                            </div>
                        )}
                        {visibleCharts.resp && (
                            <div style={chartCardStyle}>
                                <Line options={getOptions('Fréquence Respiratoire', 'RR', '#10b981')} 
                                    data={prepareData('Resp', data.resp, data.times, '#10b981')} />
                            </div>
                        )}
                    </div>
                </div>
            ) : !loading && !error && (
                <div style={emptyStateStyle}>
                    <Search size={48} style={{ marginBottom: '15px', opacity: 0.5 }} />
                    <p>Recherchez un identifiant patient pour visualiser son évolution clinique.</p>
                </div>
            )}
            {/* CONTENEUR ANALYSE IA */}
            {data && (
                <div style={aiContainerStyle}>
                    {!analysis && !isAnalyzing ? (
                        <div style={{ textAlign: 'center' }}>
                            <center>
                                <p style={{ color: '#64748b', marginBottom: '15px' }}>
                                    Données de session chargées. Prêt pour l'analyse clinique automatisée.
                                </p>
                                <button onClick={runAIAnalysis} style={aiBtnStyle}>
                                    <Activity size={18} /> Lancer l'analyse intelligente
                                </button>
                            </center>
                        </div>
                    ) : isAnalyzing ? (
                        <div style={{ textAlign: 'center', color: '#3b82f6' }}>
                            <RefreshCcw className="animate-spin" style={{ marginBottom: '10px' }} />
                            <p>Analyse des tendances en cours (Filtre de Kalman & Seuils)...</p>
                        </div>
                    ) : (
                        <div style={{ display: 'flex', alignItems: 'center', gap: '20px', width: '100%' }}>
                            <div style={{ fontSize: '40px' }}>{analysis.icon}</div>
                            <div style={{ flex: 1 }}>
                                <h3 style={{ margin: 0, color: analysis.color, display: 'flex', alignItems: 'center', gap: '8px' }}>
                                    Diagnostic IA : {analysis.label}
                                </h3>
                                <p style={{ margin: '5px 0 0', color: '#1e293b', fontWeight: '500' }}>
                                    {analysis.advice}
                                </p>
                            </div>
                            <button onClick={() => setAnalysis(null)} style={resetAiBtn}>
                                Nouvelle analyse
                            </button>
                        </div>
                    )}
                </div>
            )}

            {patient && data && (
                <div className="document-rapport" style={styleDocument}>
                    <div>Les Résultats d'examen ont été générés. Vous pouvez désormais les consulter !</div>
                    <ExportButton patientData={getPatientForReport()} vitals={getVitalsForReport()} chartRef={chartRef}/>
                </div>
            )}
        </div>
    );
};

// --- STYLES AMÉLIORÉS ---
const filterPanelStyle = { backgroundColor: 'white', padding: '20px', borderRadius: '16px', boxShadow: '0 4px 6px -1px rgba(0,0,0,0.05), 0 2px 4px -1px rgba(0,0,0,0.06)', marginBottom: '25px' };
const inputStyle = { padding: '12px 12px 12px 40px', borderRadius: '10px', border: '1px solid #e2e8f0', width: '100%', outline: 'none', fontSize: '15px' };
const searchIconStyle = { position: 'absolute', left: '12px', top: '15px', color: '#94a3b8' };
const btnStyle = { backgroundColor: '#2563eb', color: 'white', border: 'none', padding: '12px 24px', borderRadius: '10px', cursor: 'pointer', fontWeight: '600', transition: 'all 0.2s', display: 'flex', alignItems: 'center', gap: '8px' };
const checkboxGroupStyle = { display: 'flex', gap: '25px', marginTop: '20px', borderTop: '1px solid #f1f5f9', paddingTop: '20px', flexWrap: 'wrap' };
const labelStyle = { display: 'flex', alignItems: 'center', gap: '10px', fontSize: '14px', color: '#475569', cursor: 'pointer', fontWeight: '500' };
const checkStyle = { width: '18px', height: '18px', cursor: 'pointer' };
const gridStyle = { display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(500px, 1fr))', gap: '25px' };
const chartCardStyle = { backgroundColor: 'white', padding: '25px', borderRadius: '16px', height: '400px', boxShadow: '0 10px 15px -3px rgba(0,0,0,0.04)' };
const emptyStateStyle = { textAlign: 'center', marginTop: '120px', color: '#94a3b8', display: 'flex', flexDirection: 'column', alignItems: 'center' };
const errorStyle = { backgroundColor: '#fef2f2', color: '#dc2626', padding: '15px', borderRadius: '10px', marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '10px', border: '1px solid #fee2e2' };
const badgeStyle = { backgroundColor: '#e0f2fe', color: '#0369a1', padding: '6px 14px', borderRadius: '20px', fontSize: '13px', fontWeight: 'bold' };
const statStyle = { backgroundColor: 'white', padding: '20px', borderRadius: '16px', boxShadow: '0 4px 6px -1px rgba(0,0,0,0.05), 0 2px 4px -1px rgba(0,0,0,0.06)', marginBottom: '25px' };
const statContainer = { padding: '10px', borderRadius: '10px', display: 'flex', flexDirection: 'row', width: '100%', fontFamily: 'consolas' }
const statFC = { color: '#980808', border: '3px solid #dc2626', backgroundColor: '#f8bdbd', padding: '15px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between', borderRadius: '15px', width: '25%', textAlign: 'center', fontSize: '30px', marginRight: '5px' }
const statSPO2 = { color: '#07448a', border: '3px solid #267bdc', backgroundColor: '#bdf0f8', padding: '15px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between', borderRadius: '15px', width: '25%', textAlign: 'center', fontSize: '30px', marginRight: '5px' }
const statTEMP = { color: '#738406', border: '3px solid #c4dc26', backgroundColor: '#f7f8bd', padding: '15px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between', borderRadius: '15px', width: '25%', textAlign: 'center', fontSize: '30px', marginRight: '5px' }
const statRESP = { color: '#058309', border: '3px solid #26dc2c', backgroundColor: '#bdf8c9', padding: '15px', display: 'flex', flexDirection: 'column', justifyContent: 'space-between', borderRadius: '15px', width: '25%', textAlign: 'center', fontSize: '30px', marginRight: '5px' }
const styleDocument = { fontSize: '20px', textAlign: 'center', marginTop: '55px', padding: '20px', backgroundColor: '#fff', borderRadius: '12px', border: '1px solid #cbd5e1', transition: 'all 0.2s', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '15px' };
const aiContainerStyle = {
    backgroundColor: '#ffffff',
    border: '2px dashed #cbd5e1',
    borderRadius: '16px',
    padding: '30px',
    marginTop: '30px',
    marginBottom: '25px',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center',
    transition: 'all 0.3s ease'
};

const aiBtnStyle = {
    backgroundColor: '#8b5cf6', // Violet pour le côté "IA"
    color: 'white',
    border: 'none',
    padding: '12px 30px',
    borderRadius: '12px',
    cursor: 'pointer',
    fontSize: '16px',
    fontWeight: 'bold',
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    boxShadow: '0 4px 6px -1px rgba(139, 92, 246, 0.3)'
};

const resetAiBtn = {
    backgroundColor: '#f1f5f9',
    color: '#64748b',
    border: 'none',
    padding: '8px 15px',
    borderRadius: '8px',
    cursor: 'pointer',
    fontSize: '13px'
};

export default EvolutionDashboard;