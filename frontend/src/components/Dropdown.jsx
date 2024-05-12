import React, { useState, useEffect } from "react";
import api from "../api";
import { getCurrentWeek } from "../constants";
import "../styles/Dropdown.css";

const Dropdown = ({ onSelectWeek }) => {
  const [options, setOptions] = useState([]);
  const [selectedOption, setSelectedOption] = useState("");
  const [shifts, setShifts] = useState([]);

  const fetchShifts = (week) => {
    api
      .get(`/api/shifts/lastweeks/${week}`)
      .then((res) => res.data)
      .then((data) => {
        setShifts(data);
      })
      .catch((err) => alert(err));
  };

  useEffect(() => {
    const currWeek = getCurrentWeek(0);
    const nextWeek = currWeek + 1;
    fetchShifts(nextWeek);
    setSelectedOption(currWeek);
  }, []);

  useEffect(() => {
    const weekOptions = shifts.map((shift) => shift.week);
    setOptions(weekOptions);
  }, [shifts]);

  const handleChange = (event) => {
    const selectedWeek = event.target.value;
    setSelectedOption(selectedWeek);
    onSelectWeek(selectedWeek);
  };

  return (
    <select value={selectedOption} onChange={handleChange} className="dropdown">
      <option value="">Select a week</option>
      {options.map((option) => (
        <option key={option} value={option}>
          {option}
        </option>
      ))}
    </select>
  );
};

export default Dropdown;
