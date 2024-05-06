import React from "react";
import "../styles/ShiftPanel.css";
import ShiftTable from "../components/ShiftTable";

const ShiftPanel = ({ actualShift, appliedShift }) => {
  return (
    <div className="table-container">
      <ShiftTable shift={appliedShift} actual={false}/>
      <ShiftTable shift={actualShift} actual={true}/>
    </div>
  );
};

export default ShiftPanel;
