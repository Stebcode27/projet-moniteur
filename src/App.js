import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import Navbar from './components/Navbar';
import Topbar from './components/Topbar';
import ExamenTable from './pages/ExamenTable';
import Home from './pages/Home';
import About from './pages/About';
import Login from './pages/Login';
import SignIn from './pages/SignIn';
import './App.css';
import EvolutionDashboard from './pages/Monitoring';
import Loader from './components/Loader';
import Footer from './components/Footer';

// 1. Composant pour protéger les routes
const ProtectedRoute = ({ children }) => {
  const { user, loading } = useAuth();

  if (loading) return <Loader />; // Évite les redirections brutales
  if (!user) return <Navigate to="/login" />;

  return children;
};

// 2. Le Layout Principal (Sidebar + Topbar + Content)
const Layout = () => {
  return (
    <div className="app-container">
        <Topbar />
      <div className="main-wrapper">
        <Navbar />
        <main className="content">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/about" element={<About />} />
            <Route path="/examen" element={<ExamenTable />} />
            <Route path="/stats" element={<EvolutionDashboard />} />
            <Route path="/sign" element={<SignIn />} />
            <Route path="/load" element={<Loader />} />
            {/* Ajoute tes autres pages protégées ici */}
          </Routes>
          <Footer />
        </main>
      </div>
    </div>
  );
};

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          {/* Route publique (Login) */}
          <Route path="/login" element={<Login />} />
          <Route path="/sign" element={<SignIn />} />

          {/* Toutes les autres routes sont protégées par le Layout */}
          <Route 
            path="/*" 
            element={
              <ProtectedRoute>
                <Layout />
              </ProtectedRoute>
            } 
          />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;