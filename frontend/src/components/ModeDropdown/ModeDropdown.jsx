import React, { useState } from "react";
import "./ModeDropdown.css";
import { getBuiltInStrings } from "../../constants";

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
      <option value="true">{getBuiltInStrings.APPLICATION}</option>
      <option value="">{getBuiltInStrings.SCHEDULE}</option>
    </select>
  );
};

export default ModeDropdown;
