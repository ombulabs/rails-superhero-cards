import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "./useAuth.js";
import { paths } from "../../routes/paths.jsx";

export const useGoogleLogin = () => {
  const navigate = useNavigate();
  const { loginWithGoogle } = useAuth();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleGoogleSuccess = async (credentialResponse) => {
    setLoading(true);
    setError(null);

    const result = await loginWithGoogle(credentialResponse.credential);

    if (result.success) {
      navigate(paths.admin());
    } else {
      setError(result.error);
    }
    setLoading(false);
  };

  const handleGoogleError = () => {
    setError("Google login failed. Please try again.");
    setLoading(false);
  };

  return {
    handleGoogleSuccess,
    handleGoogleError,
    error,
    loading,
  };
};
