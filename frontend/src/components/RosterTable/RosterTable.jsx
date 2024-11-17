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

const RosterTable = ({ roster, application }) => {
  const currentRoster = application ? roster.application : roster.schedule;

  const rosterLabel = application
    ? getBuiltInStrings.APPLICATION
    : getBuiltInStrings.SCHEDULE;

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
          const vacation = roster.vacation;
          const sickness = roster.sickness;
          const reserveCallIn = roster.reserve_call_in_days;
          const dayOffCallIn = roster.day_off_call_in_days;
          const published = roster.published;
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
                    vacation={vacation}
                    sickness={sickness}
                    reserveCallIn={reserveCallIn}
                    dayOffCallIn={dayOffCallIn}
                    published={published}
                    day={day}
                    application={application}
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
