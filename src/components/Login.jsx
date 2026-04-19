import { useAuth } from '../context/AuthContext';

const Login = () => {
  const { login } = useAuth();

  const handleConnect = () => {
    // On simule une connexion réussie
    login({ name: "Alice", email: "alice@exemple.com" });
  };

  return <button onClick={handleConnect}>Se connecter</button>;
};