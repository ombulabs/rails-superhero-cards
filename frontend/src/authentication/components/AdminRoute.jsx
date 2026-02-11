import { Navigate } from "react-router-dom";
import { CircularProgress } from "@mui/material";
import { useAuth } from "../hooks/useAuth.js";
import { paths } from "../../routes/paths.jsx";

export function AdminRoute({ children }) {
  const { loading, isAuthenticated } = useAuth();

  if (loading) {
    return <CircularProgress />;
  }

  if (!isAuthenticated) {
    return <Navigate to={paths.login()} replace />;
  }

  return children;
}

export default AdminRoute;
