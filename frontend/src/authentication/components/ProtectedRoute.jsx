import { Navigate } from "react-router-dom";
import { CircularProgress } from "@mui/material";
import { useAuth } from "../hooks/useAuth.js";

export function ProtectedRoute({ children }) {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return <CircularProgress />;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return children;
}

export default ProtectedRoute;
