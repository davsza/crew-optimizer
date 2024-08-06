import { getStartingHours, getFinishingHours } from "../../constants";
import "./ShiftDisplay.css";

const ShiftDisplay = ({
  scheduleOfTheDay,
  appliedScheduleOfTheDay,
  highlighted,
  workDays,
  offDays,
  reserveDays,
  day,
  isAcceptedShift,
}) => {
  return (
    <div className={`outer ${highlighted ? "highlighted" : ""}`}>
      {workDays[day] === "1" || !isAcceptedShift ? (
        scheduleOfTheDay.map((shift, index) => {
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
      ) : offDays[day] === "1" ? (
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
      ) : reserveDays[day] === "1" ? (
        <div
          className="inner"
          style={{
            bottom: "0",
            left: "0",
            right: "0",
            width: "90%",
            margin: "auto",
            backgroundColor: "green",
          }}
        >
          Reserve
        </div>
      ) : (
        <div>Something unexpexted happened</div>
      )}
    </div>
  );
};

export default ShiftDisplay;
