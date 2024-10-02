import React from "react";
import "./RosterPanel.css";
import RosterTable from "../RosterTable/RosterTable";

const RosterPanel = ({ schedule, appliedSchedule }) => {
  return (
    <div className="table-container">
      <RosterTable roster={schedule} isAcceptedRoster={true} />
      <RosterTable roster={appliedSchedule} isAcceptedRoster={false} />
    </div>
  );
};

export default RosterPanel;
