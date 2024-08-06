import React from "react";
import "./ShiftTable.css";
import {
  MONTHS,
  getStartDateOfWeek,
  formatDate,
  datePlusDays,
} from "../../constants";
import ShiftDisplay from "../ShiftDisplay/ShiftDisplay";

const ShiftTable = ({ shift, isAcceptedShift }) => {
  const currentShift = isAcceptedShift
    ? shift.actual_shift
    : shift.applied_shift;

  const shiftLabel = isAcceptedShift ? "Schedule" : "Applied schedule";

  if (
    !currentShift ||
    typeof currentShift !== "string" ||
    currentShift.length !== 21
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
            {shiftLabel} for {MONTHS[startDate.getMonth()]} {startDay} -{" "}
            {MONTHS[endDate.getMonth()]} {endDay}
          </th>
        </tr>
      </thead>
      <tbody>
        {[0, 1, 2, 3, 4, 5, 6].map((day) => {
          const shiftOfTheDay = currentShift
            .substring(day * 3, day * 3 + 3)
            .split("");
          const workDays = shift.work_days;
          const offDays = shift.off_days;
          const reserveDays = shift.reserve_days;
          const displayDate = datePlusDays(startDate, day);
          const currDay = new Date();
          let additionClass = false;

          if (
            displayDate.setHours(0, 0, 0, 0) == currDay.setHours(0, 0, 0, 0)
          ) {
            additionClass = true;
          }

          return (
            <tr key={day}>
              <td key={shift} className="schedule-cell">
                <div className="flex-container">
                  <div className="vertical-text">{formatDate(displayDate)}</div>
                  <ShiftDisplay
                    scheduleOfTheDay={shiftOfTheDay}
                    highlighted={additionClass}
                    workDays={workDays}
                    offDays={offDays}
                    reserveDays={reserveDays}
                    day={day}
                    isAcceptedShift={isAcceptedShift}
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
