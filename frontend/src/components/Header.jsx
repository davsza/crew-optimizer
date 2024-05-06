import React from "react";
import "../styles/Header.css";
import { useNavigate } from "react-router-dom";

const Header = ({ userName }) => {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.clear();
    navigate("/login");
  };

  return (
    <header className="header">
      <div className="username">{userName}</div>
      <button className="logout" onClick={handleLogout}>
        Logout
      </button>
    </header>
  );
};

export default Header;
