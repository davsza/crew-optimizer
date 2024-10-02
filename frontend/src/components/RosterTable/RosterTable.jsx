import React from "react";
import "./RosterTable.css";
import {
  MONTHS,
  getStartDateOfWeek,
  formatDate,
  datePlusDays,
} from "../../constants";
import RosterDisplay from "../RosterDisplay/RosterDisplay";
import { getBuiltInStrings } from "../../constants";

const RosterTable = ({ roster, isAcceptedRoster }) => {
  const currentRoster = isAcceptedRoster ? roster.schedule : roster.application;

  const rosterLabel = isAcceptedRoster
    ? getBuiltInStrings.SCHEDULE
    : getBuiltInStrings.APPLICATION;

  if (
    !currentRoster ||
    typeof currentRoster !== "string" ||
    currentRoster.length !== 21
  ) {
    return <div>Error: Invalid schedule string.</div>;
  }

  const startDate = getStartDateOfWeek(roster.year, roster.week_number);
  const startDay = startDate.getDate();
  const endDate = new Date(startDate.getTime());
  endDate.setDate(endDate.getDate() + 6);
  const endDay = endDate.getDate();

  return (
    <table className="schedule-table">
      <thead>
        <tr>
          <th>
            {rosterLabel} for {MONTHS[startDate.getMonth()]} {startDay} -{" "}
            {MONTHS[endDate.getMonth()]} {endDay}
          </th>
        </tr>
      </thead>
      <tbody>
        {[0, 1, 2, 3, 4, 5, 6].map((day) => {
          const rosterOfTheDay = currentRoster
            .substring(day * 3, day * 3 + 3)
            .split("");
          const appliedRosterOfTheDay = roster.application
            .substring(day * 3, day * 3 + 3)
            .split("");
          const workDays = roster.work_days;
          const offDays = roster.off_days;
          const reserveDays = roster.reserve_days;
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
              <td key={roster} className="schedule-cell">
                <div className="flex-container">
                  <div className="vertical-text">{formatDate(displayDate)}</div>
                  <RosterDisplay
                    scheduleOfTheDay={rosterOfTheDay}
                    appliedScheduleOfTheDay={appliedRosterOfTheDay}
                    highlighted={additionClass}
                    workDays={workDays}
                    offDays={offDays}
                    reserveDays={reserveDays}
                    day={day}
                    isAcceptedRoster={isAcceptedRoster}
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

export default RosterTable;
