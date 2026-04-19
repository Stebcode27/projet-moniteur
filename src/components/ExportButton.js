import React from 'react';
import { Page, Text, View, Document, StyleSheet, Image, PDFDownloadLink } from '@react-pdf/renderer';

const styles = StyleSheet.create({
  page: { padding: 40, fontFamily: 'Helvetica' },
  header: { borderBottom: '2px solid #2980b9', paddingBottom: 10, marginBottom: 20 },
  title: { fontSize: 20, color: '#2980b9', fontWeight: 'bold' },
  patientInfo: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 30 },
  table: { display: 'table', width: 'auto', marginBottom: 20,fontSize: 12 },
  tableRow: { flexDirection: 'row' },
  tableCellHeader: { width: '25%', backgroundColor: '#f2f2f2', padding: 8, fontWeight: 'bold' },
  tableCell: { width: '25%', padding: 8, borderBottom: '1px solid #ccc' },
  footer: { position: 'absolute', bottom: 30, left: 40, fontSize: 10, color: 'grey' },
  patientBox: {
    padding: 15,
    marginBottom: 25,
    border: '1px solid #2980b9', // Bordure bleue pour rappeler votre dashboard
    backgroundColor: '#f9f9f9',   // Fond gris très léger
    borderRadius: 5,
  },
  row: {
    flexDirection: 'row',
    marginBottom: 5,
  },
  label: {
    fontSize: 12,
    fontWeight: 'bold',
    width: 100, // Aligne les labels proprement
    color: '#333',
  },
  value: {
    fontSize: 12,
    color: '#555',
  }
});

const ReportDocument = ({ patientData, vitals, graphImage }) => (
  <Document>
    <Page size="A4" style={styles.page}>
      {/* En-tête avec nom de votre projet */}
      <View style={styles.header}>
        <Text style={styles.title}>Life Keeper - Rapport d'Examen</Text>
      </View>

      {/* Identité Patient */}
      <View style={styles.patientBox}>
        <View style={styles.row}>
          <Text style={styles.label}>Nom :</Text>
          <Text style={styles.value}>{patientData.nom}</Text>
        </View>
        <View style={styles.row}>
          <Text style={styles.label}>ID Patient :</Text>
          <Text style={styles.value}>{patientData.id}</Text>
        </View>
        <View style={styles.row}>
          <Text style={styles.label}>Date Génertion :</Text>
          <Text style={styles.value}>{new Date().toLocaleDateString()}</Text>
        </View>
        <View style={styles.row}>
          <Text style={styles.label}>Service :</Text>
          <Text style={styles.value}>Hôpital Général de Douala</Text>
        </View>
      </View>

      <Text style={styles.title}>Analyse des Constantes Vitales</Text>

      {/* Tableau des constantes (comme sur votre écran) */}
      <View style={styles.table}>
        <View style={styles.tableRow}>
          <Text style={styles.tableCellHeader}>Constante</Text>
          <Text style={styles.tableCellHeader}>Valeur</Text>
          <Text style={styles.tableCellHeader}>Unité</Text>
          <Text style={styles.tableCellHeader}>Statut</Text>
        </View>
        {vitals.map((v, i) => (
          <View style={styles.tableRow} key={i}>
            <Text style={styles.tableCell}>{v.name}</Text>
            <Text style={styles.tableCell}>{v.value}</Text>
            <Text style={styles.tableCell}>{v.unit}</Text>
            <Text style={styles.tableCell}>{v.status}</Text>
          </View>
        ))}
      </View>

      {/* Vérifiez si l'image existe avant de l'afficher */}
      {graphImage && (
        <View style={{ marginTop: 20 }}>
          <Text>Graphique d'évolution :</Text>
          <Image src={graphImage} style={{ width: '100%', height: '200px' }} />
        </View>
      )}

      {/* Note de diagnostic IA */}
      <View style={{ marginTop: 20, padding: 10, backgroundColor: '#e8f6f3' }}>
        <Text style={{ fontSize: 12, fontWeight: 'bold' }}>Analyse IA :</Text>
        <Text style={{ fontSize: 11 }}>{patientData.aiNote}</Text>
      </View>

      <Text style={styles.footer}>Document généré automatiquement par Life Keeper.</Text>
    </Page>
  </Document>
);

const ExportButton = ({ patientData, vitals, chartRef }) => (
  <PDFDownloadLink 
    document={<ReportDocument patientData={patientData} vitals={vitals} graphImage={chartRef.current?.toBase64Image()}/>} 
    fileName={`Rapport_${patientData.id}.pdf`}
    style={{
      textDecoration: 'none',
      padding: '10px 20px',
      color: '#fff',
      backgroundColor: '#005fce',
      borderRadius: '5px',
      fontSize: '16px',
      fontWeight: 'bold',
      display: 'inline-block' // Important car c'est un lien
    }}
  >
    {({ loading }) => (loading ? 'Chargement...' : 'Télécharger le PDF')}
  </PDFDownloadLink>
);

export default ExportButton;