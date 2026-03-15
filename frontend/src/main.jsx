import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, Routes, Route } from "react-router-dom";


import App from "./App";
import ChatBubble from "./ChatBubble";
import About from "./About";
import DemoMint from "./DemoMint";
import Signup from "./Signup";
import MintNFT from "./MintNFT";
import Policies from "./Policies";
import InvestorInquiry from "./InvestorInquiry";
import UserAgreement from "./UserAgreement";
import PrivacyPolicy from "./PrivacyPolicy";
import Contact from "./Contact";
import UseCases from "./UseCases";
import WhyNow from "./WhyNow";
import Login from "./Login";
import AdminLogin from "./AdminLogin";
import AdminDashboard from "./AdminDashboard";
import Checkout from "./Checkout";
import Cart from "./Cart";
import SiteNav from "./SiteNav";
import SiteFooter from "./SiteFooter";
import { MintFlowProvider } from "./context/MintFlowContext";
import ProtectedRoute from "./ProtectedRoute";
import AdminProtectedRoute from "./AdminProtectedRoute";

function NotFound() {
  return (
    <div style={{ color: '#0A0F1F', background: '#F4F7F8', minHeight: '100vh', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
      <h1>404 - Page Not Found</h1>
      <p>The page you are looking for does not exist.</p>
      <a href="/" style={{ color: '#C9A227', fontWeight: 700, fontSize: 18 }}>Go Home</a>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <MintFlowProvider>
      <BrowserRouter>
        <>
          <SiteNav />
          <Routes>
            <Route path="/" element={<App />} />
            <Route path="/about" element={<About />} />
            <Route path="/demo-mint" element={<DemoMint />} />
            <Route path="/signup" element={<Signup />} />
            <Route path="/login" element={<Login />} />
            <Route path="/admin/login" element={<AdminLogin />} />
            <Route path="/admin/dashboard" element={<AdminProtectedRoute><AdminDashboard /></AdminProtectedRoute>} />
            <Route path="/mint" element={<ProtectedRoute><MintNFT /></ProtectedRoute>} />
            <Route path="/cart" element={<ProtectedRoute><Cart /></ProtectedRoute>} />
            <Route path="/checkout" element={<ProtectedRoute><Checkout /></ProtectedRoute>} />
            <Route path="/user-agreement" element={<UserAgreement />} />
            <Route path="/privacy-policy" element={<PrivacyPolicy />} />
            <Route path="/policies" element={<Policies />} />
            <Route path="/investor" element={<ProtectedRoute><InvestorInquiry /></ProtectedRoute>} />
            <Route path="/contact" element={<Contact />} />
            <Route path="/use-cases" element={<UseCases />} />
            <Route path="/why-now" element={<WhyNow />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
          <SiteFooter />
          <ChatBubble />
        </>
      </BrowserRouter>
    </MintFlowProvider>
  </React.StrictMode>
);
