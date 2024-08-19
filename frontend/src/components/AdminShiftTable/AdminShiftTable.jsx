import React, { useState, useEffect } from "react";
import api from "../../api";
import ShiftDisplay from "../ShiftDisplay/ShiftDisplay";
import "./AdminShiftTable.css";
import { getAdminTableHeader } from "../../constants";

const RenderShifts = ({ isAcceptedShift, shift, day }) => {
  const currentShift = isAcceptedShift
    ? shift.actual_shift
    : shift.applied_shift;
  const shiftOfTheDay = currentShift.substring(day * 3, day * 3 + 3).split("");
  const appliedShiftOfTheDay = shift.applied_shift
    .substring(day * 3, day * 3 + 3)
    .split("");
  const workDays = shift.work_days;
  const offDays = shift.off_days;
  const reserveDays = shift.reserve_days;
  return (
    <td key={day}>
      <ShiftDisplay
        scheduleOfTheDay={shiftOfTheDay}
        appliedScheduleOfTheDay={appliedShiftOfTheDay}
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

const AdminShiftTable = ({ shiftsData, isAcceptedShift }) => {
  const [usernames, setUsernames] = useState({});

  const headers = getAdminTableHeader();

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
            {headers.map((header, index) => (
              <th key={index}>{header}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {shiftsData.map((shift, index) => (
            <tr key={index}>
              <td className="username-container">
                {getUsernameById(shift.owner)}
              </td>
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
