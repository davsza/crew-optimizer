import React, { useState, useEffect } from "react";
import api from "../api";

const Dropdown = () => {
  const [options, setOptions] = useState([]);
  const [selectedOption, setSelectedOption] = useState("");
  
  const getSchedules = () => {
    api
      .get("/api/get-schedules/")
      .then((res) => res.data)
      .then((data) => {
        setShifts(data[0]);
      })
      .catch((err) => alert(err));
  };

  useEffect(() => {
    getSchedules();
  }, []);

  const handleOptionChange = (event) => {
    const selectedValue = event.target.value;
    setSelectedOption(selectedValue);

    axios
      .get(`/api/option/${selectedValue}`)
      .then((response) => {

      })
      .catch((error) => {
        console.error("Error fetching data for selected option:", error);
      });
  };

  return (
    <div>
      <select value={selectedOption} onChange={handleOptionChange}>
        <option value="">Select an option</option>
        {options.map((option) => (
          <option key={option.id} value={option.id}>
            {option.name}
          </option>
        ))}
      </select>
    </div>
  );
};

export default Dropdown;
