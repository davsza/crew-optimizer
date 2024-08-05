import React from "react";
import "./ShiftPanel.css";
import ShiftTable from "../ShiftTable/ShiftTable";

const ShiftPanel = ({ actualShift, appliedShift }) => {
  return (
    <div className="table-container">
      <ShiftTable shift={actualShift} isAcceptedShift={true} />
      <ShiftTable shift={appliedShift} isAcceptedShift={false} />
    </div>
  );
};

export default ShiftPanel;
