import React from "react";
import { Routes, Route } from "react-router-dom";
import { UserProvider } from "../UserContext";
import { Header } from "../components/Header";
import Landing from "../pages/Landing/index";
import Statistics from "../pages/Stats/index";
import GetQrCode from "../pages/GetQrCode/index";
import GetURL from "../pages/GetURL/index";
import Shortner from "../pages/Shortner/index";
import Login from "../pages/Login";
import Register from "../pages/Register";
import Dashboard from "../pages/Dashboard"



export const Navigation = () => {
    return (
        <UserProvider>
            <Header />
            <Routes>
                <Route path="/" element={<Landing />} />
                <Route path="/stats" element={<Statistics />} />
                <Route path="/get-qr-code" element={<GetQrCode />} />
                <Route path="/get-original-url" element={<GetURL />} />
                <Route path="/shorten-link" element={<Shortner />}  />
                <Route path="/login" element={<Login />}  />
                <Route path="/register" element={<Register />}  />
                <Route path="/link-history" element={<Dashboard />} />
            </Routes>
        </UserProvider>
    );
};
