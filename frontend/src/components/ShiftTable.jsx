import React from "react";
import "../styles/ShiftTable.css";
import { MONTHS, DAYS } from "../constants";

const ShiftTable = ({ shift, actual }) => {
  const appliedShift = actual ? shift.actual_shift : shift.applied_shift;

  if (
    !appliedShift ||
    typeof appliedShift !== "string" ||
    appliedShift.length !== 21
  ) {
    return <div>Error: Invalid schedule string.</div>;
  }

  const getStartingHours = (index) => {
    const hours = [6, 10, 14];
    return hours[index];
  };

  const getFinishinggHours = (index) => {
    const hours = [14, 18, 22];
    return hours[index];
  };

  function getStartDateOfWeek(year, weekNumber) {
    const januaryFirst = new Date(year, 0, 1);
    const firstDayOfYear = januaryFirst.getDay() || 7;
    const daysToAdd = (weekNumber - 1) * 7 - (firstDayOfYear - 1);
    const startDate = new Date(year, 0, 1 + daysToAdd);
    startDate.setDate(startDate.getDate() - startDate.getDay() + 1);
    return startDate;
  }

  const startDate = getStartDateOfWeek(shift.year, shift.week);
  const startDay = startDate.getDate();
  const endDate = new Date(startDate.getTime());
  endDate.setDate(endDate.getDate() + 6);
  const endDay = endDate.getDate();
  return (
    <table className="schedule-table">
      <thead>
        <tr>{actual ? "aasd" : "asd"}</tr>
        <tr>
          <th>
            {MONTHS[startDate.getMonth()]} {startDay} -{" "}
            {MONTHS[endDate.getMonth()]} {endDay}
          </th>
          <th>Working hours</th>
        </tr>
      </thead>
      <tbody>
        {[0, 1, 2, 3, 4, 5, 6].map((day) => {
          const index = appliedShift
            .substring(day * 3, day * 3 + 3)
            .indexOf("1");
          const from = getStartingHours(index);
          const to = getFinishinggHours(index);
          return (
            <tr key={day}>
              <td>{DAYS[day]}</td>
              <td key={shift} className="schedule-cell">
                <div className="outer">
                  {index !== -1 ? (
                    <div
                      className="inner"
                      style={{
                        left: `${(from / 24) * 100}%`,
                        width: `${((to - from) / 24) * 100}%`,
                        backgroundColor: "#007bff",
                      }}
                    >
                      {from} - {to}
                    </div>
                  ) : (
                    <div
                      className="inner"
                      style={{
                        bottom: "0",
                        left: "0",
                        right: "0",
                        width: "90%",
                        margin: "auto",
                        backgroundColor: "red",
                      }}
                    >
                      Day off
                    </div>
                  )}
                </div>
              </td>
            </tr>
          );
        })}
      </tbody>
    </table>
  );
};

export default ShiftTable;
