import React, { useState, useEffect } from "react";
import api from "../../api";
import {
  getCurrentWeek,
  getStartDateOfWeek,
  getEndDateOfWeek,
  formatDate,
  getBuiltInStrings,
} from "../../constants";
import "./Dropdown.css";

const Dropdown = ({ year, finalShifts, onSelectWeek }) => {
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
    const nextWeek = getCurrentWeek(1);
    const appliableWeek = getCurrentWeek(2);
    if (finalShifts) {
      fetchShifts(nextWeek);
      setSelectedOption(currWeek);
    } else {
      fetchShifts(appliableWeek);
      setSelectedOption(appliableWeek);
    }
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
      <option value="">{getBuiltInStrings.SELECT_WEEK_STRING}</option>
      {options.map((option) => {
        const startDate = getStartDateOfWeek(year, option);
        const endDate = getEndDateOfWeek(year, option);
        return (
          <React.Fragment key={option}>
            <option value={option}>
              {formatDate(startDate)} - {formatDate(endDate)}
            </option>
          </React.Fragment>
        );
      })}
    </select>
  );
};

export default Dropdown;
