import React from "react";
import "./RosterPanel.css";
import RosterTable from "../RosterTable/RosterTable";

const RosterPanel = ({ schedule, application }) => {
  return (
    <div className="table-container">
      <RosterTable roster={schedule} application={false} />
      <RosterTable roster={application} application={true} />
    </div>
  );
};

export default RosterPanel;
