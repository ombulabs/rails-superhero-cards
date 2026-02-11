import { useEffect, useState } from "react";
import { tokenStorage } from "../utils/tokenStorage";
import { authService } from "../services/api.js";
import { AuthContext } from "./authContext.js";

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  const checkAuth = async () => {
    const token = tokenStorage.get();
    if (!token) {
      setLoading(false);
      return;
    }

    try {
      const userData = await authService.getCurrentUser(token);
      setUser(userData);
      setIsAuthenticated(true);
    } catch (error) {
      if (error.response?.status === 401 || error.response?.status === 403) {
        tokenStorage.remove();
        setUser(null);
        setIsAuthenticated(false);
      } else {
        console.error("Failed to verify authentication:", error.message);
        setUser(null);
        setIsAuthenticated(false);
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    checkAuth();
  }, []);

  const loginWithGoogle = async (googleToken) => {
    try {
      const response = await authService.loginWithGoogle(googleToken);
      tokenStorage.set(response.access_token);
      const userData = await authService.getCurrentUser(response.access_token);
      setUser(userData);
      setIsAuthenticated(true);
      return { success: true };
    } catch (error) {
      return {
        success: false,
        error: error.response?.data?.detail || "Login failed",
      };
    }
  };

  const logout = () => {
    tokenStorage.remove();
    setUser(null);
    setIsAuthenticated(false);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        isAuthenticated,
        loginWithGoogle,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}
