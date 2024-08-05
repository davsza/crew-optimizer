import React, { useState, useEffect } from "react";
import api from "../../api";
import ShiftDisplay from "../ShiftDisplay/ShiftDisplay";
import "./AdminShiftTable.css";

const RenderShifts = ({ isAcceptedShift, shift, day, user }) => {
  const currentShift = isAcceptedShift
    ? shift.applied_shift
    : shift.actual_shift;
  const shiftOfTheDay = currentShift.substring(day * 3, day * 3 + 3).split("");
  const workDays = shift.work_days;
  const offDays = shift.off_days;
  const reserveDays = shift.reserve_days;
  console.log(user, isAcceptedShift, currentShift);
  return (
    <td key={day}>
      <ShiftDisplay
        shiftOfTheDay={shiftOfTheDay}
        highlighted={false}
        workDays={workDays}
        offDays={offDays}
        reserveDays={reserveDays}
        day={day}
        isAcceptedShift={isAcceptedShift}
      ></ShiftDisplay>
    </td>
  );
};

const AdminShiftTable = ({ shiftsData, mode }) => {
  const [usernames, setUsernames] = useState({});

  const isAcceptedShift = mode === "true" ? true : false;

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
  }, []);

  function getUsernameById(userId) {
    return usernames[userId] || null;
  }

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
              {[0, 1, 2, 3, 4, 5, 6].map((dayIndex) => (
                <RenderShifts
                  key={`${dayIndex}-${isAcceptedShift}`}
                  isAcceptedShift={isAcceptedShift}
                  shift={shift}
                  day={dayIndex}
                  user={getUsernameById(shift.owner)}
                />
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default AdminShiftTable;
