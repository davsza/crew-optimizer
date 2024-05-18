import React from "react";
import "../styles/ShiftTable.css";
import {
  MONTHS,
  getStartDateOfWeek,
  formatDate,
  datePlusDays,
} from "../constants";

const ShiftTable = ({ shift, isAcceptedShift }) => {
  const appliedShift = isAcceptedShift
    ? shift.actual_shift
    : shift.applied_shift;

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

  const getFinishingHours = (index) => {
    const hours = [14, 18, 22];
    return hours[index];
  };

  const startDate = getStartDateOfWeek(shift.year, shift.week);
  const startDay = startDate.getDate();
  const endDate = new Date(startDate.getTime());
  endDate.setDate(endDate.getDate() + 6);
  const endDay = endDate.getDate();
  return (
    <table className="schedule-table">
      <thead>
        <tr>
          <th>
            {MONTHS[startDate.getMonth()]} {startDay} -{" "}
            {MONTHS[endDate.getMonth()]} {endDay}
          </th>
        </tr>
      </thead>
      <tbody>
        {[0, 1, 2, 3, 4, 5, 6].map((day) => {
          const shifts = appliedShift.substring(day * 3, day * 3 + 3).split("");
          const hasShift = shifts.includes("1");

          return (
            <tr key={day}>
              <td key={shift} className="schedule-cell">
                <div>{formatDate(datePlusDays(startDate, day))}</div>
                <div className="outer">
                  {!hasShift ? (
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
                  ) : (
                    shifts.map((shift, index) => {
                      const from = getStartingHours(index);
                      const to = getFinishingHours(index);
                      const style = {
                        color: shift === "1" ? "#ffffff" : "#007bff",
                        backgroundColor:
                          shift === "1" ? "#007bff" : "transparent",
                        border: shift !== "1" ? "1px solid #007bff" : "none",
                        left: `${(from / 24) * 100}%`,
                        width: `${((to - from) / 24) * 100}%`,
                      };
                      return (
                        <div key={index} className="inner" style={style}>
                          {from} - {to}
                        </div>
                      );
                    })
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
