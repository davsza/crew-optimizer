import React from "react";
import "../styles/ShiftTable.css";
import {
  MONTHS,
  getStartDateOfWeek,
  formatDate,
  datePlusDays,
} from "../constants";
import ShiftDisplay from "./ShiftDisplay";

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
          const displayDate = datePlusDays(startDate, day);
          const currDay = new Date();
          let additionClass = false;

          if (displayDate.getDate() == currDay.getDate()) {
            additionClass = true;
          }

          return (
            <tr key={day}>
              <td key={shift} className="schedule-cell">
                <div className="flex-container">
                  <div className="vertical-text">{formatDate(displayDate)}</div>
                  <ShiftDisplay
                    hasShift={hasShift}
                    shifts={shifts}
                    highlighted={additionClass}
                  />
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
