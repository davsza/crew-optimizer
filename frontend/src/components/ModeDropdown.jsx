import React, { useState } from "react";
import "../styles/ModeDropdown.css";

const ModeDropdown = ({ onChange }) => {
  const [selectedValue, setSelectedValue] = useState("true");

  const handleChange = (event) => {
    const value = event.target.value;
    setSelectedValue(value);
    onChange(value);
  };

  return (
    <select
      value={selectedValue}
      onChange={handleChange}
      className="modedropdown"
    >
      <option value="true">True</option>
      <option value="">False</option>
    </select>
  );
};

export default ModeDropdown;
