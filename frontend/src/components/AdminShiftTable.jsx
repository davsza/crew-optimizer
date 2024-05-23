import React, { useState, useEffect } from "react";
import api from "../api";
import ShiftDisplay from "./ShiftDisplay";
import "../styles/AdminShiftTable.css";

const AdminShiftTable = ({ shiftsData, finalShift }) => {
  const [usernames, setUsernames] = useState({});

  const fetchUserName = () => {
    api
      .get(`/api/user/`)
      .then((res) => res.data)
      .then((data) => {
        setUsernames(data);
      })
      .catch((err) => alert(err));
  };

  useEffect(() => {
    fetchUserName();
    console.log(shiftsData);
  }, []);

  function getUsernameById(userId) {
    return usernames[userId] || null;
  }

  const renderShifts = (appliedShift, day) => {
    const shifts = appliedShift.substring(day * 3, day * 3 + 3).split("");
    const hasShift = shifts.includes("1");
    return (
      <td key={day}>
        <ShiftDisplay hasShift={hasShift} shifts={shifts}></ShiftDisplay>
      </td>
    );
  };

  return (
    <div className="table-container">
      <table className="shift-table">
        <thead>
          <tr>
            <th></th>
            <th>Monday</th>
            <th>Tuesday</th>
            <th>Wednesday</th>
            <th>Thursday</th>
            <th>Friday</th>
            <th>Saturday</th>
            <th>Sunday</th>
          </tr>
        </thead>
        <tbody>
          {shiftsData.map((shift, index) => (
            <tr key={index}>
              <td>{getUsernameById(shift.owner)}</td>
              {[0, 1, 2, 3, 4, 5, 6].map((dayIndex) =>
                renderShifts(
                  finalShift ? shift.applied_shift : shift.actual_shift,
                  dayIndex
                )
              )}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default AdminShiftTable;
