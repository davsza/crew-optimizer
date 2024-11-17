import React, { useState, useEffect } from "react";
import api from "../../api";
import RosterDisplay from "../RosterDisplay/RosterDisplay";
import "./AdminRosterTable.css";
import { getAdminTableHeader } from "../../constants";

const RenderRosters = ({ application, roster, day }) => {
  const currentRoster = application ? roster.application : roster.schedule;
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
  return (
    <td key={day}>
      <RosterDisplay
        scheduleOfTheDay={rosterOfTheDay}
        appliedScheduleOfTheDay={appliedRosterOfTheDay}
        highlighted={false}
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
      ></RosterDisplay>
    </td>
  );
};

const AdminRosterTable = ({ rostersData, application }) => {
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
      <table className="roster-table">
        <thead>
          <tr>
            {headers.map((header, index) => (
              <th key={index}>{header}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rostersData.map((roster, index) => (
            <tr key={index}>
              <td className="username-container">
                {getUsernameById(roster.owner)}
              </td>
              {[0, 1, 2, 3, 4, 5, 6].map((dayIndex) => (
                <RenderRosters
                  key={`${dayIndex}-${application}`}
                  application={application}
                  roster={roster}
                  day={dayIndex}
                />
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default AdminRosterTable;
