import { getStartingHours, getFinishingHours } from "../constants";
import "../styles/ShiftDisplay.css";

const ShiftDisplay = ({ hasShift, shifts, highlighted }) => {
  return (
    <div className={`outer ${highlighted ? "highlighted" : ""}`}>
      {!hasShift ? (
        <div
          className="inner"
          style={{
            bottom: "0",
            left: "0",
            right: "0",
            width: "90%",
            margin: "auto",
            backgroundColor: "red",
          }}
        >
          Day off
        </div>
      ) : (
        shifts.map((shift, index) => {
          const from = getStartingHours(index);
          const to = getFinishingHours(index);
          const style = {
            color: shift === "1" ? "#ffffff" : "#007bff",
            backgroundColor: shift === "1" ? "#007bff" : "transparent",
            border: shift !== "1" ? "1px solid #007bff" : "none",
            left: `${(from / 24) * 100}%`,
            width: `${((to - from) / 24) * 100}%`,
          };
          return (
            <div key={index} className="inner" style={style}>
              {from} - {to}
            </div>
          );
        })
      )}
    </div>
  );
};

export default ShiftDisplay;
