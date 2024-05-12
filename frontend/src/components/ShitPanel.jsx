import React from "react";
import "../styles/ShiftPanel.css";
import ShiftTable from "../components/ShiftTable";

const ShiftPanel = ({ actualShift, appliedShift }) => {
  return (
    <div className="table-container">
      <ShiftTable shift={actualShift} actual={true}/>
      <ShiftTable shift={appliedShift} actual={false}/>
    </div>
  );
};

export default ShiftPanel;
