import React from "react";
import "./ShiftPanel.css";
import ShiftTable from "../ShiftTable/ShiftTable";

const ShiftPanel = ({ schedule, appliedSchedule }) => {
  return (
    <div className="table-container">
      <ShiftTable shift={schedule} isAcceptedShift={true} />
      <ShiftTable shift={appliedSchedule} isAcceptedShift={false} />
    </div>
  );
};

export default ShiftPanel;
