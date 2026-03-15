import React from "react";
import { Navigate, useLocation } from "react-router-dom";
import { isUserAuthenticated } from "./authStorage";

export default function ProtectedRoute({ children }) {
  const location = useLocation();

  if (!isUserAuthenticated()) {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  }

  return children;
}
