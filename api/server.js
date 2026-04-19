const express = require('express');
const cors = require('cors');
const dgram = require('dgram');
const mysql = require('mysql2');

const app = express();
app.use(cors());
app.use(express.json({ limit: '1000mb' })); 
app.use(express.urlencoded({ limit: '1000mb', extended: true }));

const db = mysql.createConnection({
    host: 'localhost',
    user: 'root',
    password: '',
    database: 'hopital'
});

db.connect((err) => {
    if (err) {
        console.error('Erreur de connexion MySQL:', err.message);
        return;
    }
    console.log('Connecté à la base de données MySQL !');
});

//UDP
const udpServer = dgram.createSocket('udp4');
const UDP_PORT = 45454;

udpServer.on('message', (msg, rinfo) => {
    if (msg.toString() === 'MONITOR_REQUEST') {
        console.log(`Moniteur détecté : ${rinfo.address}`);
        const response = Buffer.from('MONITOR_ALIVE');
        udpServer.send(response, rinfo.port, rinfo.address);
    }
});

udpServer.bind(UDP_PORT, () => {
    console.log(`Service de découverte actif sur le port ${UDP_PORT}`);
});

// --- 2. RÉCEPTION DES DONNÉES (API REST) ---
app.post('/api/monitoring/session', async (req, res) => {
    const { patient, medecin, exam, donnees } = req.body;

    console.log({patient, medecin, exam});

    try {
        const idServiceCorrect = exam.service;
        const idSalle = exam.salle;

        // 2. GESTION DU MÉDECIN (Enregistre ou met à jour le service)
        const sqlMedecin = `
            INSERT INTO personnel_medical (id_pers, nom, service_id) 
            VALUES (?, ?, ?) 
            ON DUPLICATE KEY UPDATE service_id = VALUES(service_id)
        `;
        // Si medecin est vide dans le JSON, on utilise un ID par défaut
        const idDoctor = medecin && medecin !== "" ? medecin : "DOC_TEMP";
        await db.promise().execute(sqlMedecin, [idDoctor, "Médecin Garde", idServiceCorrect]);

        // 3. GESTION DU PATIENT (Enregistre ou met à jour les constantes physiques)
        const sqlPatient = `
            INSERT INTO patient (id, nom, age, sexe, poids, taille) 
            VALUES (?, ?, ?, ?, ?, ?) 
            ON DUPLICATE KEY UPDATE nom=VALUES(nom), poids=VALUES(poids), taille=VALUES(taille)
        `;
        const sexeChar = patient.sexe === 'Masculin' ? 'M' : 'F';
        await db.promise().execute(sqlPatient, [
            patient.id, patient.nom, patient.age, sexeChar, patient.poids, patient.taille
        ]);

        // 4. CALCUL ET PRÉPARATION DU JSON POUR session_monitoring
        const mesuresValides = donnees.filter(d => d !== null);
        const statsEtCourbes = {
            stats: {
                hr_avg: Math.round(mesuresValides.reduce((acc, d) => acc + d.hr, 0) / mesuresValides.length),
                spo2_avg: Math.round(mesuresValides.reduce((acc, d) => acc + d.spo2, 0) / mesuresValides.length),
                temp_avg: (mesuresValides.reduce((acc, d) => acc + d.temp, 0) / mesuresValides.length).toFixed(1),
                resp_avg: Math.round(mesuresValides.reduce((acc, d) => acc + d.resp, 0) / mesuresValides.length)
            },
            curves: {
                hr: mesuresValides.map(d => d.hr),
                spo2: mesuresValides.map(d => d.spo2),
                temp: mesuresValides.map(d => d.temp),
                resp: mesuresValides.map(d => d.resp),
                times: mesuresValides.map(d => d.timestamp)
            }
        };

        // 5. INSERTION DE LA SESSION
        const sqlSession = `
            INSERT INTO session_monitoring 
            (date_examen, heure_debut, heure_fin, id_personnel, id_patient, donnees_patient, salle) 
            VALUES (CURDATE(), ?, ?, ?, ?, ?, ?)
        `;
        const hDebut = exam.debut_exam ? exam.debut_exam.trim() : "00:00:00";
        const hFin = new Date().toLocaleTimeString('fr-FR', { hour12: false });

        await db.promise().execute(sqlSession, [
            hDebut, hFin, idDoctor, patient.id, JSON.stringify(statsEtCourbes), idSalle
        ]);

        res.status(201).json({ message: "Succès : Médecin, Patient et Session synchronisés." });

    } catch (error) {
        console.error("❌ Erreur de synchronisation :", error);
        res.status(500).json({ error: "Détail : " + (error.sqlMessage || "Erreur serveur") });
    }
});

app.get('/api/patients', (req, res) => {
    const sql = "SELECT * FROM patient order by id desc";
    
    db.query(sql, (err, results) => {
        if (err) {
            console.error(err);
            return res.status(500).json({ error: "Erreur lors de la récupération" });
        }
        res.json(results);
    });
});

app.get('/api/salle', (req, res) => {
    const sql = "select salle from session_monitoring order by id desc";

    db.query(sql, (err, results) => {
        if(err){
            console.error(err);
            return res.status(500).json({error: "Erreur lors de la récupération"});
        }
        res.json(results[0]);
        console.log(results[0]);
    });
});

app.post('/api/doctors/signup', async (req, res) => {
    const query = "insert into personnel_medical (id_pers, nom, email, telephone, password, service_id) values (?, ?, ?, ?, ?, ?)";
    const {id, fullName, email, phone, password, id_service} = req.body;

    try {
        const [existingDoctor] = await db.promise().query("select email from personnel_medical where email = ?", [email]);

        if (existingDoctor.length>0){
            return res.status(400).json({message: "Cet email est déjà utilisé."});
        }

        await db.promise().execute(query, [
            id,
            fullName,
            email,
            phone,
            password,
            id_service
        ]);

        res.status(201).json({message: "Compte du medecin crée avec succès."});
    } catch (error) {
        console.error("Erreur d'inscription:", error.sqlMessage);
        res.status(500).json({message: "Erreur serveur lors de l'inscription."});
    }
})

app.get('/api/login', (req, res) => {
    const sql = "select * from personnel_medical"

    db.query(sql, (err, results) => {
        if (err) {
            console.error(err);
            return res.status(500).json({ error: "Erreur lors de la récupération" });
        }
        res.json(results);
    });
});

// Nouvelle route pour lister les sessions d'un patient
app.get('/api/monitoring/sessions/:patientId', (req, res) => {
    const { patientId } = req.params;
    // On récupère uniquement les IDs des sessions
    const sql = "SELECT id, date_examen FROM session_monitoring WHERE id_patient = ? ORDER BY id DESC";
    
    db.query(sql, [patientId], (err, results) => {
        if (err) return res.status(500).json({ error: "Erreur SQL" });
        res.json(results);
    });
});

app.get('/api/monitoring/session-detail/:id', (req, res) => {
    const patientId = req.params.id;

    // On récupère la DERNIÈRE session enregistrée pour ce patient
    const sql = "SELECT donnees_patient FROM session_monitoring WHERE id_patient = ? ORDER BY id DESC LIMIT 1";

    db.query(sql, [patientId], (err, results) => {
        if (err) return res.status(500).json({ message: "Erreur SQL" });
        if (results.length === 0) return res.status(404).json({ message: "Session non trouvée" });

        try {
            const row = results[0];
            const fullData = typeof row.donnees_patient === 'string' 
                ? JSON.parse(row.donnees_patient) 
                : row.donnees_patient;

            res.json(fullData);
        } catch (e) {
            res.status(500).json({ message: "Erreur de lecture des données JSON" });
        }
    });
});

app.get('/api/monitoring/session/:id_pat/:id_sess', (req, res) => {
    const patientId = req.params.id_pat;
    const sessionId = req.params.id_sess;

    const sql = "SELECT donnees_patient FROM session_monitoring WHERE id_patient = ? and id = ? ORDER BY id DESC LIMIT 1";

    db.query(sql, [patientId, sessionId], (err, results) => {
        if (err) return res.status(500).json({ message: "Erreur SQL" });
        if (results.length === 0) return res.status(404).json({ message: "Session non trouvée" });

        try {
            const row = results[0];
            const fullData = typeof row.donnees_patient === 'string' 
                ? JSON.parse(row.donnees_patient) 
                : row.donnees_patient;

            res.json(fullData);
        } catch (e) {
            res.status(500).json({ message: "Erreur de lecture des données JSON" });
        }
    });
})

app.get('/api/monitoring/patient/:id', (req, res) => {
    const patientId = req.params.id;

    const sql = "select * from patient where id = ?";

    db.query(sql, [patientId], (err, results) => {
        if(err) return res.status(500).json({message: "Erreur SQL"});
        if(results.length===0) return res.status(404).json({message: "Session Non Trouvée"});

        res.json(results[0]);
    });
});

app.listen(5000, () => console.log("Serveur API sur le port 5000"));