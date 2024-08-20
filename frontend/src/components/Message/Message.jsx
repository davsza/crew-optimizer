import React from "react";
import "./Message.css"; // Import the CSS file
import { formatTimestampToFormattedTime } from "../../constants";

const Message = ({ text, date, isSentByUser, index }) => {
  return (
    <>
      <div className={`message ${isSentByUser ? "sent" : "received"}`}>
        <p className="message-text">{text}</p>
      </div>
      <div className={`date-display ${isSentByUser ? "sent" : "received"}`}>
        {formatTimestampToFormattedTime(date)}
      </div>
    </>
  );
};

export default Message;
