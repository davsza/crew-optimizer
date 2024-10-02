import { getRosterDisplayParameters } from "../../constants";
import "./RosterDisplay.css";
import { getBuiltInStrings } from "../../constants";

const RosterDisplay = ({
  scheduleOfTheDay,
  appliedScheduleOfTheDay,
  highlighted,
  workDays,
  offDays,
  reserveDays,
  day,
  isAcceptedRoster,
}) => {
  return (
    <div className={`outer ${highlighted ? "highlighted" : ""}`}>
      {workDays[day] === "1" || !isAcceptedRoster ? (
        scheduleOfTheDay.map((roster, index) => {
          const { from, to, application, style } = getRosterDisplayParameters(
            roster,
            index,
            appliedScheduleOfTheDay
          );
          return (
            <div
              key={index}
              className={`inner ${
                application === "1" && isAcceptedRoster ? "application" : ""
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

export default RosterDisplay;
