import React from "react";
import "./RosterComponent.css";

const RosterComponent = ({ content, backgroundColor }) => {
  return (
    <div
      className="inner"
      style={{
        bottom: "0",
        left: "0",
        right: "0",
        width: "90%",
        margin: "auto",
        backgroundColor: backgroundColor,
      }}
    >
      {content}
    </div>
  );
};

export default RosterComponent;
