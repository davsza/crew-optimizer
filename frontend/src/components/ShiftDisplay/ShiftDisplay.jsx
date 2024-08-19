import { getShiftDisplayParameters } from "../../constants";
import "./ShiftDisplay.css";
import { getBuiltInStrings } from "../../constants";

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
          const { from, to, appliedShift, style } = getShiftDisplayParameters(
            shift,
            index,
            appliedScheduleOfTheDay
          );
          return (
            <div
              key={index}
              className={`inner ${
                appliedShift === "1" && isAcceptedShift ? "application" : ""
              }`}
              style={style}
            >
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
          {getBuiltInStrings.DAY_OFF}
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
          {getBuiltInStrings.RESERVE}
        </div>
      ) : (
        <div>{getBuiltInStrings.NO_SCHEDULE_TO_DISPLAY}</div>
      )}
    </div>
  );
};

export default ShiftDisplay;
